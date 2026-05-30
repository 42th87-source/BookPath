"""
전국대학별학과정보표준데이터 → KDC별 학과 정보 맵 생성
출력: data/career_map.json

구조 (웹에서 "이 책과 관련된 학과" 섹션에 바로 사용):
{
  "400": {
    "kdc_name": "자연과학",
    "departments": [
      {
        "name": "물리학과",
        "subjects": ["고전역학", "양자역학", "전자기학", "광학", "수리물리"],
        "careers": ["물리학연구원", "반도체공학기술자"]
      }, ...
    ]
  }
}
"""
import sys, json, os, re
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

# ── KDC별 대표 학과 검색 키워드 (순서 = 우선순위) ─────────────────────────────
KDC_DEPT_KEYWORDS = {
    "000": ["문헌정보학과", "도서관정보학과", "기록관리학과", "미디어정보학과", "정보관리학과"],
    "100": ["철학과", "윤리학과", "심리학과", "상담심리학과", "인지과학과"],
    "200": ["종교학과", "신학과", "불교학과", "선교학과", "기독교학과"],
    "300": ["경영학과", "경제학과", "법학과", "사회학과", "사회복지학과",
            "정치외교학과", "교육학과", "행정학과"],
    "400": ["물리학과", "화학과", "생물학과", "수학과", "천문우주학과",
            "지구환경과학과", "통계학과"],
    "500": ["컴퓨터학과", "소프트웨어학과", "전자공학과", "기계공학과",
            "의학과", "간호학과", "환경공학과", "건축학과"],
    "600": ["음악학과", "미술학과", "디자인학과", "체육학과", "영화학과",
            "연극영화학과", "무용학과"],
    "700": ["영어영문학과", "국어국문학과", "중어중문학과", "일어일문학과", "언어학과"],
    "800": ["국어국문학과", "문예창작학과", "한국어문학과", "국문학과", "문화콘텐츠학과"],
    "900": ["역사학과", "고고학과", "지리학과", "한국사학과", "문화인류학과"],
}

# 직업 정보가 비어 있을 때 사용하는 KDC별 기본 직업
KDC_DEFAULT_CAREERS = {
    "000": ["사서", "데이터분석가", "정보보안전문가"],
    "100": ["철학연구원", "심리상담사", "윤리학자"],
    "200": ["종교학연구원", "사회복지사", "신학자"],
    "300": ["공무원", "경제연구원", "사회복지사"],
    "400": ["자연과학연구원", "과학교사", "의약연구원"],
    "500": ["개발자", "공학기술자", "의사"],
    "600": ["예술가", "문화기획자", "체육교사"],
    "700": ["번역가", "언어교사", "통역사"],
    "800": ["작가", "국어교사", "출판편집자"],
    "900": ["역사연구원", "박물관큐레이터", "지리학연구원"],
}

KDC_NAMES = {
    "000": "총류·컴퓨터", "100": "철학·심리", "200": "종교",
    "300": "사회과학",    "400": "자연과학",  "500": "기술·공학",
    "600": "예술·스포츠", "700": "언어",      "800": "문학",
    "900": "역사·지리",
}

MAX_DEPTS    = 5
MAX_SUBJECTS = 6
MAX_CAREERS  = 4


SUBJ_STOPWORDS = {
    '특론', '특강', '연구', '응용', '기초', '개론', '실습', '이해',
    '특수', '과제', '논문', '세미나', '고급', '고전', '인턴십', '인텁십',
    '구조', '테스트', '입문', '강독', '실험', '방법론',
}

def clean_subjects(raw: str) -> list:
    """'+' 구분 교과목명 → 핵심 한글 교과목 리스트"""
    if not raw or raw == 'nan':
        return []
    parts = re.split(r'\+|＋', raw)
    cleaned = []
    for p in parts:
        p = p.strip()
        # 괄호 내용 제거, 영숫자 제거
        p = re.sub(r'\([^)]*\)', '', p).strip()
        p = re.sub(r'[A-Za-z\d\-\s]+', '', p).strip()
        p = re.sub(r'\s+', '', p)
        # 3글자 이상이고 stopword가 아닌 것만
        if len(p) >= 3 and p not in SUBJ_STOPWORDS:
            cleaned.append(p)
    # 짧은(핵심) 것 우선, 중복 제거
    seen, result = set(), []
    for s in sorted(cleaned, key=len):
        if s not in seen:
            seen.add(s)
            result.append(s)
    return result[:MAX_SUBJECTS]


def clean_careers(raw: str) -> list:
    """'+' 구분 직업명 → 짧고 핵심적인 직업 리스트"""
    if not raw or raw == 'nan':
        return []
    parts = re.split(r'\+', raw)
    cleaned = []
    for p in parts:
        p = p.strip()
        if 2 <= len(p) <= 18:
            cleaned.append(p)
    seen, result = set(), []
    for c in sorted(cleaned, key=len):
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result[:MAX_CAREERS]


def find_dept_row(df: pd.DataFrame, keyword: str):
    """학과명이 keyword와 정확히 일치하거나 keyword로 끝나는 행 반환.
    교양·협동·복합 학과보다 단독 학과 우선."""
    # 1순위: 정확히 일치
    exact = df[df['학과명'] == keyword]
    # 2순위: keyword로 끝나는 학과 (예: '화학과'로 끝나는 것만)
    ends  = df[df['학과명'].str.endswith(keyword, na=False)] if len(exact) == 0 else exact
    pool  = ends if len(ends) > 0 else df[df['학과명'].str.contains(keyword, na=False, regex=False)]

    if len(pool) == 0:
        return None

    # 괄호·특수문자 없는 단순 학과명 우선, 그 다음 주요교과목 있는 것 우선
    simple  = pool[~pool['학과명'].str.contains(r'[()（）]', na=False, regex=True)]
    if len(simple) > 0:
        pool = simple
    with_subj = pool[pool['주요교과목명'].notna()]
    return with_subj.iloc[0] if len(with_subj) > 0 else pool.iloc[0]


def main():
    base     = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base, '..', '전국대학별학과정보표준데이터.csv')
    out_path = os.path.join(base, '..', 'data', 'career_map.json')

    print("CSV 로드 중...")
    df = pd.read_csv(csv_path, encoding='cp949', dtype=str,
                     usecols=['학과상태명', '학과명', '주요교과목명', '관련직업명'])
    df = df[df['학과상태명'] == '기존'].reset_index(drop=True)
    print(f"  유효 학과 수: {len(df):,}개")

    career_map = {}

    for kdc, keywords in KDC_DEPT_KEYWORDS.items():
        departments = []
        used_names = set()

        for kw in keywords:
            if len(departments) >= MAX_DEPTS:
                break
            row = find_dept_row(df, kw)
            if row is None:
                continue
            dept_name = str(row['학과명']).strip()
            if dept_name in used_names:
                continue
            used_names.add(dept_name)

            subjects = clean_subjects(str(row.get('주요교과목명', '')))
            careers  = clean_careers(str(row.get('관련직업명', '')))

            # 직업이 없으면 KDC 기본값으로 보충
            if not careers:
                careers = KDC_DEFAULT_CAREERS.get(kdc, ["연구원", "교사"])[:2]

            departments.append({
                "name":     dept_name,
                "subjects": subjects,
                "careers":  careers,
            })

        career_map[kdc] = {
            "kdc_name":    KDC_NAMES[kdc],
            "departments": departments,
        }

        dept_names = [d['name'] for d in departments]
        print(f"  [{kdc}] {KDC_NAMES[kdc]}: {dept_names}")

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(career_map, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {out_path}")


if __name__ == '__main__':
    main()
