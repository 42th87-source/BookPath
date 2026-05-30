"""
Claude API로 도서 태그 + KDC 분류 생성
입력: data/raw_books.json
출력: data/books_tagged.json

환경변수 ANTHROPIC_API_KEY 필요
"""
import sys, json, os, time
sys.stdout.reconfigure(encoding='utf-8')
import anthropic

MODEL      = "claude-haiku-4-5"
BATCH_SIZE = 10
DELAY      = 0.4
MAX_BOOKS  = None   # None이면 전체 처리

SYSTEM_PROMPT = """당신은 학생 도서 큐레이터입니다. 도서 정보를 보고 JSON 배열을 반환하세요.

출력 형식 (이 JSON만 출력, 다른 텍스트 금지):
[
  {
    "idx": 0,
    "kdc": "400",
    "student_tags": ["태그1", "태그2", "태그3"],
    "career_tags": ["진로1", "진로2"]
  }
]

규칙:
- kdc: KDC 대분류 코드 3자리 (000/100/200/300/400/500/600/700/800/900 중 하나)
  000=총류·컴퓨터, 100=철학·심리, 200=종교, 300=사회과학·경제·법,
  400=자연과학·수학, 500=기술·의학·공학, 600=예술·스포츠,
  700=언어, 800=문학·소설·시, 900=역사·지리·전기
- student_tags: 고등학생 눈높이 키워드 3~5개 (2~7글자 한국어 명사)
- career_tags: 관련 직업·전공 2~3개 (한국어 명사)
- 설명이 없으면 제목으로 추론"""

def build_prompt(batch):
    lines = []
    for i, b in enumerate(batch):
        lines.append(f"[{i}] 제목: {b['title']}")
        if b.get('author'):
            lines.append(f"    저자: {b['author']}")
        desc = b.get('description', '')
        if desc:
            lines.append(f"    설명: {desc[:200]}")
        lines.append("")
    return "\n".join(lines)

def main():
    base     = os.path.dirname(os.path.abspath(__file__))
    in_path  = os.path.join(base, '..', 'data', 'raw_books.json')
    out_path = os.path.join(base, '..', 'data', 'books_tagged.json')

    if not os.path.exists(in_path):
        print("오류: data/raw_books.json 없음 — fetch_books_api.py를 먼저 실행하세요")
        return

    with open(in_path, encoding='utf-8') as f:
        books = json.load(f)
    if MAX_BOOKS:
        books = books[:MAX_BOOKS]

    # 이미 처리된 책 재시작 지원
    done_path = out_path + '.progress'
    done_set  = set()
    if os.path.exists(done_path):
        with open(done_path, encoding='utf-8') as f:
            done_set = set(json.load(f))

    client = anthropic.Anthropic()
    total  = len(books)
    print(f"처리 대상: {total}권 (이미 완료: {len(done_set)}권)")

    for i in range(0, total, BATCH_SIZE):
        batch_idx  = list(range(i, min(i + BATCH_SIZE, total)))
        batch_books = [books[j] for j in batch_idx if j not in done_set]
        if not batch_books:
            continue

        print(f"  [{i+1}~{min(i+BATCH_SIZE, total)}/{total}]", end=" ", flush=True)
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_prompt(batch_books)}]
            )
            raw = resp.content[0].text.strip()
            s, e = raw.find('['), raw.rfind(']') + 1
            results = json.loads(raw[s:e])

            for res in results:
                local_idx = res.get('idx', 0)
                if local_idx < len(batch_books):
                    global_idx = batch_idx[local_idx]
                    books[global_idx]['kdc']          = res.get('kdc', '')
                    books[global_idx]['student_tags'] = res.get('student_tags', [])
                    books[global_idx]['career_tags']  = res.get('career_tags', [])
                    done_set.add(global_idx)
            print(f"완료")

        except Exception as e:
            print(f"오류: {e}")

        # 중간 저장 (중단 시 재시작 가능)
        if i % 100 == 0:
            with open(done_path, 'w', encoding='utf-8') as f:
                json.dump(list(done_set), f)
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=2)

        time.sleep(DELAY)

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    if os.path.exists(done_path):
        os.remove(done_path)

    tagged = sum(1 for b in books if b.get('student_tags'))
    print(f"\n완료: {tagged}/{total}권 태그+KDC 생성 → {out_path}")

if __name__ == '__main__':
    main()
