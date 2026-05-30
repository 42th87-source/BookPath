"""
Google Gemini로 도서 KDC 분류 + 태그 생성 (유료 API 사용)

사전 준비:
  1. Google AI Studio 또는 Google Cloud에서 API 키 발급
  2. pip install google-genai
  3. 환경변수 GEMINI_API_KEY 설정 (또는 아래 변수에 직접 입력)

입력: data/raw_books.json
출력: data/books_tagged.json
"""
import sys, json, os, time, re
sys.stdout.reconfigure(encoding='utf-8')

from google import genai
from google.genai import types

# ── 설정 ──────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "여기에_API_키_입력")
MODEL          = "models/gemini-2.5-flash"
BATCH_SIZE     = 10
DELAY          = 1.0   # 유료 API — 분당 60회 이상 허용, 1초 간격
MAX_BOOKS      = None  # None이면 전체 처리, 테스트 시 30 등으로 제한

SYSTEM_PROMPT = """당신은 한국 청소년 진로 도서 큐레이터입니다. 도서 정보를 보고 JSON 배열만 반환하세요.

출력 형식 (이 JSON 배열만 출력, 다른 텍스트 없이):
[
  {
    "idx": 0,
    "kdc": "440",
    "student_tags": ["생명의신비", "유전자탐구", "진화론", "생태계"],
    "career_tags": ["생물학자", "생명공학자"]
  }
]

규칙:

1. kdc: KDC 분류 코드 3자리 (반드시 10의 배수)
   000=총류·컴퓨터, 010=도서관·정보학,
   100=철학, 110=형이상학, 120=인식론, 150=심리학, 160=윤리학,
   200=종교, 210=불교, 220=기독교, 230=이슬람,
   300=사회과학, 310=정치, 320=법, 330=경제, 340=경영, 350=교육, 360=복지,
   400=자연과학, 410=수학, 420=물리, 430=화학, 440=생물, 460=천문, 470=지구과학,
   500=기술·공학, 510=공학, 520=건축, 530=기계, 540=전기·전자, 570=의학, 580=약학,
   600=예술, 610=음악, 620=미술, 630=사진·영상, 650=스포츠, 660=디자인,
   700=언어, 710=한국어, 720=중국어, 730=일본어, 740=영어, 750=독일어, 760=프랑스어,
   800=문학, 810=한국문학, 820=일본문학, 830=중국문학, 840=영어문학, 850=독일문학, 860=프랑스문학,
   900=역사·지리, 910=동양사, 920=서양사, 930=지리, 990=전기·자서전

2. student_tags: 고등학생 눈높이 한국어 키워드 3~4개 (2~8글자 명사, 책 내용을 잘 설명하는 단어)

3. career_tags: 아래 표준 직업 목록에서 이 책과 가장 관련 깊은 직업 2~3개 선택.
   목록에 없는 직업은 추가 불가.

   [표준 직업 목록]
   인문·사회: 철학자, 윤리학자, 심리상담사, 임상심리사, 뇌과학자, 사회학자, 사회복지사,
              경제학자, 금융전문가, 경영컨설턴트, 마케터, 창업가, 회계사,
              변호사, 판사, 검사, 기자·언론인, 정치인, 외교관, 공무원,
              교사, 교육학자, 진로상담사,
              종교학자, 신학자, 문화인류학자,
              역사학자, 고고학자, 박물관큐레이터, 지리학자, 여행작가, 문화기획자
   이공계:    수학자, 통계학자, 데이터과학자, 데이터분석가,
              물리학자, 반도체공학자,
              화학자, 화학공학자, 소재공학자,
              생물학자, 생명공학자, 유전공학자,
              천문학자, 지구과학자, 기상학자, 환경과학자, 해양학자, 지질학자,
              의사, 간호사, 약사, 의학연구원, 수의사, 영양사,
              기계공학자, 환경공학자, 건축가, 도시계획가, 전기공학자, 전자공학자,
              로봇공학자, 항공우주공학자, AI연구원, 소프트웨어개발자, 정보보안전문가
   예술·언어: 소설가, 시인, 번역가, 통역사, 언어학자, 국어교사, 영어교사, 출판편집자,
              방송작가, 시나리오작가, 만화가·웹툰작가,
              음악가, 작곡가, 지휘자, 음악치료사, 화가, 조각가, 큐레이터, 미술치료사, 배우,
              그래픽디자이너, UX디자이너, 패션디자이너, 인테리어디자이너,
              사진작가, 영상감독, 영화감독, 방송PD,
              스포츠선수, 스포츠지도자, 사서

4. 설명이 없으면 제목과 저자로 추론
5. 공지·안내문·행사 등 비도서는 kdc를 "SKIP"으로 표시"""


def build_prompt(batch: list) -> str:
    lines = []
    for i, b in enumerate(batch):
        lines.append(f"[{i}] 제목: {b['title']}")
        if b.get('author'):
            lines.append(f"    저자: {b['author']}")
        if b.get('description'):
            lines.append(f"    설명: {b['description'][:200]}")
        lines.append("")
    return "\n".join(lines)


def parse_response(text: str) -> list:
    """LLM 응답에서 JSON 배열 추출"""
    text = text.strip()
    text = re.sub(r'```(?:json)?', '', text).strip()
    s = text.find('[')
    e = text.rfind(']') + 1
    if s == -1 or e == 0:
        return []
    return json.loads(text[s:e])


def main():
    if GEMINI_API_KEY == "여기에_API_키_입력":
        print("오류: GEMINI_API_KEY를 설정해주세요.")
        print("  방법 1: 스크립트 상단 GEMINI_API_KEY 변수에 직접 입력")
        print("  방법 2: 환경변수 → set GEMINI_API_KEY=your_key_here")
        print("  키 발급: https://aistudio.google.com")
        return

    base      = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.path.abspath('scripts')
    in_path   = os.path.join(base, '..', 'data', 'raw_books.json')
    out_path  = os.path.join(base, '..', 'data', 'books_tagged.json')
    prog_path = out_path + '.progress'

    with open(in_path, encoding='utf-8') as f:
        books = json.load(f)
    if MAX_BOOKS:
        books = books[:MAX_BOOKS]
    total = len(books)

    # 이전 진행분 복원
    done_set = set()
    if os.path.exists(prog_path):
        with open(prog_path, encoding='utf-8') as f:
            done_set = set(json.load(f))
        print(f"이전 진행분 복원: {len(done_set)}권 완료")

    if os.path.exists(out_path) and done_set:
        with open(out_path, encoding='utf-8') as f:
            saved = json.load(f)
        # SKIP 포함 원본 길이 맞춰 병합
        for b in saved:
            orig_idx = next((i for i, x in enumerate(books)
                             if x['title'] == b['title']), None)
            if orig_idx is not None:
                books[orig_idx] = b

    client = genai.Client(api_key=GEMINI_API_KEY)

    remaining = total - len(done_set)
    print(f"처리 대상: {total}권 | 완료: {len(done_set)}권 | 남은 배치: {(remaining + BATCH_SIZE - 1) // BATCH_SIZE}개")
    print(f"예상 소요: ~{(remaining // BATCH_SIZE * DELAY) // 60:.0f}분\n")

    skipped_total = 0

    for i in range(0, total, BATCH_SIZE):
        batch_indices = [j for j in range(i, min(i + BATCH_SIZE, total))
                         if j not in done_set]
        if not batch_indices:
            continue

        batch_books = [books[j] for j in batch_indices]
        print(f"  [{i+1}~{min(i+BATCH_SIZE, total)}/{total}]", end=" ", flush=True)

        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=build_prompt(batch_books),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                ),
            )
            results = parse_response(resp.text)

            for res in results:
                local_idx = res.get('idx', 0)
                if local_idx >= len(batch_books):
                    continue
                global_idx = batch_indices[local_idx]
                kdc = res.get('kdc', '')

                if kdc == 'SKIP':
                    books[global_idx]['kdc']          = 'SKIP'
                    books[global_idx]['student_tags'] = []
                    books[global_idx]['career_tags']  = []
                    skipped_total += 1
                else:
                    books[global_idx]['kdc']          = kdc
                    books[global_idx]['student_tags'] = res.get('student_tags', [])
                    books[global_idx]['career_tags']  = res.get('career_tags', [])

                done_set.add(global_idx)

            print(f"완료 ({len(results)}건) | 비도서 누적: {skipped_total}건")

        except Exception as e:
            print(f"오류: {e}")
            time.sleep(10)

        # 50배치마다 중간 저장
        batch_num = i // BATCH_SIZE + 1
        if batch_num % 50 == 0:
            _save(books, out_path, done_set, prog_path)
            print(f"  ✓ 중간 저장 ({len(done_set)}/{total})")

        time.sleep(DELAY)

    # SKIP 제거 후 최종 저장
    books_final = [b for b in books if b.get('kdc') != 'SKIP']
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(books_final, f, ensure_ascii=False, indent=2)
    if os.path.exists(prog_path):
        os.remove(prog_path)

    tagged = sum(1 for b in books_final if b.get('student_tags'))
    print(f"\n완료: {tagged}/{len(books_final)}권 태그 생성 → {out_path}")
    print(f"비도서 제거: {skipped_total}건")

    from collections import Counter
    kdc_names = {"000":"총류","100":"철학","200":"종교","300":"사회과학",
                 "400":"자연과학","500":"기술과학","600":"예술",
                 "700":"언어","800":"문학","900":"역사"}
    counter = Counter(b['kdc'] for b in books_final if b.get('kdc'))
    print("\nKDC 분포:")
    for kdc in sorted(counter):
        bar = '█' * (counter[kdc] // 30)
        print(f"  {kdc} {kdc_names.get(kdc,''):6s} {counter[kdc]:4d}권 {bar}")


def _save(books, out_path, done_set, prog_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    with open(prog_path, 'w', encoding='utf-8') as f:
        json.dump(list(done_set), f)


if __name__ == '__main__':
    main()
