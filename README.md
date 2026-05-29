# BookPath: 공공데이터 기반 진로 확장형 디지털 서가 탐색 서비스

> AI 추천 시대, 도서관의 '우연한 발견' 경험을 온라인에서 구현하기

---

## 🎯 프로젝트 개요

**BookPath**는 공공데이터(사서추천도서, KDC 분류, 대학학과정보)와 AI(Gemini)를 활용하여 학생들이 책을 통해 진로를 탐색할 수 있도록 돕는 웹 서비스입니다.

- **문제**: 학생들이 책을 탐색하는 경험 감소, 추천 시스템의 다양성 부족
- **해결책**: 마인드맵 기반 분야 탐색 + "다른 시각으로 보기" 기능 + 진로 연결

---

## 📊 사용 공공데이터

| 데이터 | 출처 | 용도 | 크기 |
|--------|------|------|------|
| **사서추천도서** | 국립어린이청소년도서관 API | 핵심 도서 데이터 | 7,085권 |
| **KDC 표준분류체계** | 교육청 공공데이터 | 마인드맵 구조 | 10대+세부분류 |
| **전국대학별학과정보** | 공공데이터포털 | 학과+교과목+진로 | 50,000행 |

---

## 🎨 주요 기능

### 1️⃣ KDC 마인드맵 탐색
- D3.js로 구현한 대화형 마인드맵
- 도서관식 분류 체계: 총류 → 자연과학 → 물리학 → 고전역학
- 분야별 도서 수 표시

### 2️⃣ 책 카드 + 학과 정보
- 책의 제목, 저자, 설명
- AI 생성 태그 (학생 친화적 키워드)
- **관련 학과 3개** (배우는 교과목 + 진로)

### 3️⃣ "다른 시각으로 보기"
- 현재 분야와 의미 있게 연결된 다른 분야 추천
- 예: 물리학 → "과학이 만드는 기술" (공학) or "과학과 사회" (사회과학)

### 4️⃣ 개인 독서 분석
- 읽은 책 등록 → 분야 비율 시각화
- 태그 워드클라우드
- 미탐색 분야 추천

### 5️⃣ 진로 연결 정보
- 책 분야 → 대학 학과 → 구체적 직업
- CareerNet 연동 (예정)

---

## 📁 프로젝트 구조

```
BookPath/
├── data/
│   ├── raw_books.json                    # 원본 도서 데이터 (7,085권)
│   ├── books_tagged.json                 # AI 태그 + KDC 분류 완료
│   ├── kdc_tree.json                     # KDC 마인드맵 구조
│   ├── career_map.json                   # 학과 정보 맵
│   └── side_shelf_map.json               # 분야 간 의미 있는 연결
├── scripts/
│   ├── generate_tags_gemini.py           # Gemini API로 태그 생성
│   ├── build_career_map.py               # 학과 정보 생성
│   └── tag_books_local.py                # 규칙 기반 태그 (백업)
├── web/                                   # 웹 서비스 (구현 중)
│   ├── index.html                        # 마인드맵 탐색 (기능 1)
│   ├── book-card.html                    # 책 카드 + 학과 정보 (기능 2,5)
│   ├── my-shelf.html                     # 개인 분석 (기능 4)
│   ├── css/style.css
│   ├── js/
│   │   ├── app.js                        # 메인 로직
│   │   ├── mindmap.js                    # D3.js 마인드맵
│   │   ├── analysis.js                   # 개인 분석 (Chart.js)
│   │   └── career.js                     # 진로 정보 표시
│   └── data/                             # data/ 폴더 심링크
├── analysis/
│   ├── problem_analysis.ipynb            # 공공데이터 분석 노트북
│   └── graphs/                           # 분석 그래프 PNG
├── docs/
│   ├── 공공데이터 분석 대회 개요.md
│   ├── DATA_SPEC.md                      # 데이터 명세서
│   └── 기능별_데이터_상세.md             # 상세 가이드
├── .github/workflows/
│   └── tag-books.yml                     # CI/CD: 자동 태깅 (예정)
├── .gitignore
└── README.md (this file)
```

---

## 🚀 설치 및 실행

### 전제 조건
- Python 3.10+
- 필요 패키지: `google-genai`, `pandas`

### 1단계: 저장소 복제
```bash
git clone https://github.com/42th87/BookPath.git
cd BookPath
```

### 2단계: 의존성 설치
```bash
pip install google-genai pandas
```

### 3단계: Gemini API 설정
```bash
# 방법 1: 환경변수
export GEMINI_API_KEY=your_api_key_here

# 방법 2: scripts/generate_tags_gemini.py 수정
GEMINI_API_KEY = "your_api_key_here"
```

### 4단계: 태그 생성 (선택사항, 이미 완료됨)
```bash
python scripts/generate_tags_gemini.py
```

### 5단계: 웹 실행
```bash
# Python HTTP 서버
cd web
python -m http.server 8000

# 또는 Live Server 플러그인 (VS Code)
# http://localhost:8000 접속
```

---

## 📊 데이터 처리 파이프라인

```
공공데이터 수집
    ↓
[Step 1] 사서추천도서 API → raw_books.json
[Step 2] 표준분류체계 → kdc_tree.json
[Step 3] 대학학과정보 + KDC 매핑 → career_map.json
[Step 4] Gemini AI 태깅 → books_tagged.json
[Step 5] 수작업 설계 → side_shelf_map.json
    ↓
웹 서비스 구현
    ↓
배포 (GitHub Pages)
```

---

## 🔄 CI/CD 자동 태깅 (GitHub Actions)

`.github/workflows/tag-books.yml`:
```yaml
# Gemini API 키를 GitHub Secrets에 저장
# Settings → Secrets → GEMINI_API_KEY

# 이후 push 시 자동으로:
# 1. scripts/generate_tags_gemini.py 실행
# 2. books_tagged.json 갱신
# 3. 결과 자동 커밋
```

---

## 🛠️ 기술 스택

| 역할 | 기술 |
|------|------|
| 데이터 분석 | Python, Pandas, Jupyter |
| AI 태깅 | Google Gemini API |
| 웹 프레임워크 | HTML/CSS/JavaScript (순수) |
| 마인드맵 | D3.js v7 |
| 차트 | Chart.js |
| 워드클라우드 | WordCloud.js |
| 데이터 저장 | JSON 정적 파일 |
| 배포 | GitHub Pages |
| CI/CD | GitHub Actions |

---

## 📝 문서

- [`기능별_데이터_상세.md`](기능별_데이터_상세.md) — 공공데이터 + 가공 + 웹 활용 상세 가이드
- [`DATA_SPEC.md`](DATA_SPEC.md) — 데이터 명세서 및 API 정의
- [`기능정리.md`](기능정리.md) — 5가지 기능 체크리스트

---

## 📅 진행 상황

| Phase | 내용 | 소요일 | 상태 |
|-------|------|--------|------|
| Phase 1 | 문제 분석 + 시각화 | 2~3일 | ✓ 완료 |
| Phase 2 | 데이터 전처리 + AI 태깅 | 3~4일 | 🔄 진행 중 (내일 완료) |
| Phase 3 | 웹 MVP (마인드맵, 책카드, 분석) | 5~7일 | ⏳ 예정 |
| Phase 4 | 고도화 + UX 테스트 | 2~3일 | ⏳ 예정 |
| Phase 5 | 보고서 + PPT + 시연 | 2~3일 | ⏳ 예정 |

---

## 👤 개발자

42th87 (고등학생 개발자)  
학교메일: 42th87@djshs.djsch.kr

---

**프로젝트**: 2025년 교육 공공데이터 분석 대회 출품작
