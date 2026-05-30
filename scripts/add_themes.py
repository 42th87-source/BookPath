"""
도서 themes 추가 스크립트

generate_tags_gemini.py 실행 후 books_tagged.json에
'themes' 필드(분야 초월 연결 주제어 2개)를 추가합니다.

사전 준비:
  1. generate_tags_gemini.py 완료 후 data/books_tagged.json 있어야 함
  2. pip install google-genai (이미 설치됨)
  3. 환경변수 GEMINI_API_KEY 설정

소요 시간: 약 5~7분 (30권/배치, 1,500회 제한 이하)

입력: data/books_tagged.json
출력: data/books_tagged.json (themes 필드 추가)
"""
import sys, json, os, time, re
sys.stdout.reconfigure(encoding='utf-8')

from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "여기에_API_키_입력")
MODEL      = "models/gemini-2.5-flash"
BATCH_SIZE = 30
DELAY      = 2.0  # 배치가 크므로 2초

# 15개 고정 테마 목록
THEMES_LIST = [
    "환경","윤리","생명","기술","사회","인권",
    "경제","역사","창의","교육","과학","예술",
    "철학","심리","문화"
]

# KDC 첫자리별 제외 테마 (자기 분야는 연결 테마로 쓰지 않음)
KDC_EXCLUDE = {
    "0": ["기술"],
    "1": ["철학", "심리"],
    "2": ["문화"],
    "3": ["사회", "경제", "교육", "인권"],
    "4": ["과학"],
    "5": ["기술", "과학"],
    "6": ["예술", "창의"],
    "7": [],
    "8": ["예술", "창의", "문화"],
    "9": ["역사"],
}

SYSTEM_PROMPT = """당신은 도서 큐레이터입니다.
각 도서가 '자신의 분야를 넘어 다른 분야와 어떻게 연결될 수 있는지'를 나타내는 주제어 2개를 선택하세요.

출력 형식 (JSON 배열만, 다른 텍스트 없이):
[{"idx": 0, "themes": ["환경", "윤리"]}, ...]

판단 기준 (우선순위):
1. description — 책이 실제로 무엇을 다루는지 핵심 근거
2. title       — description이 없을 때 참고
3. kdc / 제외 테마 — 이 분야 자체를 나타내는 테마는 선택 금지

선택 가능 테마 (반드시 이 중에서만):
환경/윤리/생명/기술/사회/인권/경제/역사/창의/교육/과학/예술/철학/심리/문화

예시:
- 화학 반응과 환경 오염을 다루는 책  → ["환경", "생명"]
- AI의 인간 정체성 문제를 다루는 책  → ["철학", "윤리"]
- 조선시대 경제를 다루는 역사책      → ["경제", "사회"]
- 스포츠 심리학 책                   → ["심리", "교육"]"""


def build_prompt(batch: list) -> str:
    lines = []
    for i, b in enumerate(batch):
        kdc_key = (b.get('kdc') or '0')[0]
        excluded = KDC_EXCLUDE.get(kdc_key, [])
        lines.append(f"[{i}] 제목: {b['title']}")
        if b.get('description'):
            lines.append(f"    설명: {b['description'][:300]}")
        lines.append(f"    KDC: {b.get('kdc','')} | 제외 테마: {', '.join(excluded) if excluded else '없음'}")
        lines.append("")
    return "\n".join(lines)


def parse_response(text: str) -> list:
    text = re.sub(r'```(?:json)?', '', text).strip()
    s = text.find('['); e = text.rfind(']') + 1
    if s == -1 or e == 0:
        return []
    try:
        return json.loads(text[s:e])
    except Exception:
        return []


def main():
    if GEMINI_API_KEY == "여기에_API_키_입력":
        print("오류: GEMINI_API_KEY를 설정해주세요.")
        print("  set GEMINI_API_KEY=your_key_here")
        return

    base    = os.path.dirname(os.path.abspath(__file__))
    path    = os.path.join(base, '..', 'data', 'books_tagged.json')

    with open(path, encoding='utf-8') as f:
        books = json.load(f)

    # 이미 themes 있는 책은 건너뜀 (재실행 시 이어서 가능)
    todo = [(i, b) for i, b in enumerate(books) if 'themes' not in b]
    total_batches = (len(todo) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"전체: {len(books)}권 | themes 추가 필요: {len(todo)}권")
    print(f"배치 크기: {BATCH_SIZE}권 | 예상 배치 수: {total_batches}개")
    print(f"예상 소요: ~{total_batches * DELAY / 60:.1f}분\n")

    client = genai.Client(api_key=GEMINI_API_KEY)

    for batch_num, batch_start in enumerate(range(0, len(todo), BATCH_SIZE), 1):
        batch_items   = todo[batch_start:batch_start + BATCH_SIZE]
        batch_books   = [b for _, b in batch_items]
        batch_indices = [i for i, _ in batch_items]

        print(f"  배치 {batch_num}/{total_batches} [{batch_start+1}~{min(batch_start+BATCH_SIZE, len(todo))}권]",
              end=" ", flush=True)

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
                raw_themes = res.get('themes', [])
                # 유효한 테마만 저장, 최대 2개
                valid = [t for t in raw_themes if t in THEMES_LIST][:2]
                books[global_idx]['themes'] = valid

            print(f"완료 ({len(results)}건)")

        except Exception as e:
            print(f"오류: {e}")
            time.sleep(10)

        # 50배치마다 중간 저장
        if batch_num % 50 == 0:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=2)
            print(f"  ✓ 중간 저장 ({sum(1 for b in books if 'themes' in b)}/{len(books)})")

        time.sleep(DELAY)

    # themes 없는 책에 빈 배열 기본값
    for b in books:
        if 'themes' not in b:
            b['themes'] = []

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    done = sum(1 for b in books if b.get('themes'))
    print(f"\n완료: {done}/{len(books)}권 themes 추가 → {path}")

    # 테마 분포 출력
    from collections import Counter
    counter = Counter(t for b in books for t in b.get('themes', []))
    print("\nthemes 분포:")
    for theme, cnt in sorted(counter.items(), key=lambda x: -x[1]):
        bar = '█' * (cnt // 50)
        print(f"  {theme:4s}  {cnt:4d}권  {bar}")


if __name__ == '__main__':
    main()
