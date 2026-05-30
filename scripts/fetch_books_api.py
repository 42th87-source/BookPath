"""
사서 추천 도서 API 수집 스크립트 (한국문화정보원 api.kcisa.kr)
출력: data/raw_books.json  (총 7,085건)

API 필드: title, description, rights(저자/역자), language, regDate
※ KDC 필드 없음 → generate_tags.py에서 Claude로 추론
"""
import sys, json, os, time
import subprocess
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

API_KEY   = "36b40ca4-b075-4caf-89f0-adc904053698"
BASE_URL  = "https://api.kcisa.kr/openapi/service/rest/meta2/NLCFsase"
PAGE_SIZE = 100
DELAY     = 0.4   # 초당 2.5 요청

def fetch_xml(page_no):
    url = f"{BASE_URL}?serviceKey={API_KEY}&numOfRows={PAGE_SIZE}&pageNo={page_no}"
    result = subprocess.run(
        ["curl", "-s", "--max-time", "20", url],
        capture_output=True
    )
    return result.stdout.decode('utf-8', errors='replace')

def parse_text(el, tag):
    child = el.find(tag)
    return (child.text or "").strip() if child is not None else ""

def parse_author(rights_str):
    """'홍길동 글 ; 김철수 그림 ; 이영희 옮김//' → '홍길동'"""
    if not rights_str:
        return ""
    parts = rights_str.split(';')
    first = parts[0].strip()
    for suffix in [' 글', ' 지음', ' 저', ' 씀', ' 글·그림']:
        if suffix in first:
            return first.replace(suffix, '').strip()
    return first.split('//')[0].strip()

def main():
    base    = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base, '..', 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'raw_books.json')

    # 1페이지로 총 건수 확인
    xml_str   = fetch_xml(1)
    root      = ET.fromstring(xml_str)
    total     = int(root.find('.//totalCount').text)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"총 {total}건 / {total_pages}페이지 수집 시작")

    all_books = []

    for page in range(1, total_pages + 1):
        print(f"  페이지 {page}/{total_pages} ...", end=" ", flush=True)
        try:
            xml_str = fetch_xml(page)
            root    = ET.fromstring(xml_str)
            items   = root.findall('.//item')
        except Exception as e:
            print(f"오류: {e}, 재시도 생략")
            time.sleep(2)
            continue

        for item in items:
            rights = parse_text(item, 'rights')
            all_books.append({
                "title":       parse_text(item, 'title'),
                "author":      parse_author(rights),
                "rights":      rights,
                "description": parse_text(item, 'description'),
                "language":    parse_text(item, 'language'),
                "reg_date":    parse_text(item, 'regDate'),
                "kdc":         "",      # generate_tags.py에서 추론
                "student_tags": [],
                "career_tags":  []
            })

        print(f"누적 {len(all_books)}건")
        time.sleep(DELAY)

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {len(all_books)}권 → {out_path}")

if __name__ == '__main__':
    main()
