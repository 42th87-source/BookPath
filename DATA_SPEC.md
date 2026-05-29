# 데이터 명세서 & 기능-데이터 매핑

---

## 데이터 파일 목록 및 구조

### 1. `data/raw_books.json` (입력)
**용도**: 원본 도서 데이터  
**크기**: 7,085권

```json
[
  {
    "title": "제목",
    "author": "저자",
    "rights": "권리정보",
    "description": "도서소개",
    "language": "ko",
    "reg_date": "2024-01-01"
  }
]
```

---

### 2. `data/books_tagged.json` (처리됨, 핵심)
**용도**: 웹서비스의 모든 책 데이터. 기능 2,3,4,5에 사용  
**상태**: ✓ 완성 (Gemini Web에서 받은 데이터 병합 필요)

```json
[
  {
    "title": "Love That Dog",
    "author": "샤론 크리치",
    "description": "...",
    "kdc": "800",                           // KDC 대분류 (기능 1,2,5)
    "student_tags": ["시쓰기", "감정표현", "성장"],  // 웹 UI (기능 2,4)
    "career_tags": ["국어교사", "작가", "출판편집자"]  // 웹 UI (기능 2,5)
  }
]
```

**데이터 요구사항**:
- `kdc`: "000"~"900" (필수)
- `student_tags`: 3~4개, 2~8글자 (필수)
- `career_tags`: 2~3개 (필수)
- SKIP 제거됨

---

### 3. `data/kdc_tree.json` (처리됨, 마인드맵용)
**용도**: 기능 1 - KDC 기반 마인드맵 탐색  
**상태**: ✓ 완성

```json
{
  "id": "root",
  "name": "도서 탐색",
  "code": "",
  "children": [
    {
      "id": "000",
      "name": "총류·컴퓨터·도서관",
      "code": "000",
      "children": [
        {"id": "010", "name": "도서관학", "code": "010", "children": []},
        {"id": "020", "name": "컴퓨터", "code": "020", "children": []}
      ]
    },
    {
      "id": "400",
      "name": "자연과학",
      "code": "400",
      "children": [
        {"id": "410", "name": "수학", "code": "410", "children": []},
        {"id": "420", "name": "물리학", "code": "420", "children": []},
        {"id": "430", "name": "화학", "code": "430", "children": []}
      ]
    }
    // ... 900까지
  ]
}
```

---

### 4. `data/career_map.json` (처리됨, 학과연결용)
**용도**: 기능 5 - 진로/학과 정보 표시  
**상태**: ✓ 완성 (학과명, 교과목, 진로 모두 포함)

```json
{
  "400": {
    "kdc_name": "자연과학",
    "departments": [
      {
        "name": "물리학과",
        "subjects": ["고전역학", "양자역학", "전자기학", ...],
        "careers": ["물리학연구원", "반도체공학기술자", ...]
      },
      {
        "name": "화학과",
        "subjects": ["일반화학", "유기화학", "나노화학", ...],
        "careers": ["자연과학연구원", "신소재연구원", ...]
      }
    ]
  },
  // ... 000~900 모두
}
```

**웹에서 사용**:
```javascript
let dept_info = careerMap[book.kdc];
// dept_info.kdc_name → 분야명
// dept_info.departments → 관련 학과 5개
//   ├─ name → 학과명
//   ├─ subjects → 배우는 교과목 6개
//   └─ careers → 관련 진로 4개
```

---

### 5. `data/side_shelf_map.json` (처리됨, 연결용)
**용도**: 기능 3 - "다른 시각으로 보기" (옆 서가 이동)  
**상태**: ✓ 완성 (30개 연결)

```json
{
  "description": "KDC 간 의미 있는 연결 맵. 각 KDC에서 3개의 다른 시각을 제시.",
  "connections": {
    "400": [
      {
        "target_kdc": "500",
        "label": "과학이 만드는 기술",
        "reason": "기초과학 발견이 공학·의학 기술로 이어집니다",
        "example_tags": ["응용과학", "바이오기술", "신소재"]
      },
      {
        "target_kdc": "300",
        "label": "과학과 사회",
        "reason": "과학 기술은 사회·윤리·정책과 연결됩니다",
        "example_tags": ["과학윤리", "기후정책", "생명윤리"]
      },
      {
        "target_kdc": "800",
        "label": "과학과 인문학",
        "reason": "과학의 역사와 철학을 문학·에세이로 만납니다",
        "example_tags": ["과학사", "과학철학", "과학산책"]
      }
    ],
    // ... 모든 KDC (000~900)
  }
}
```

**웹에서 사용**:
```javascript
let connections = sideShelfMap.connections[book.kdc];
// 임의로 3개 중 1개 선택
let target = connections[0];
// target.target_kdc에서 student_tags 매칭하는 책 3개 랜덤 추천
```

---

## 기능-데이터 매핑

### 기능 1: KDC 기반 마인드맵 탐색
| 요소 | 데이터 | 처리 |
|------|--------|------|
| **노드 구조** | `kdc_tree.json` | 그대로 D3.js로 렌더링 |
| **각 KDC의 책 수** | `books_tagged.json` 그룹핑 | `books.filter(b => b.kdc.startsWith('4'))` |
| **선택 시 표시** | KDC 코드 | → 기능 2로 이동 |

**웹파일**: `index.html` + `js/mindmap.js` (D3.js)

---

### 기능 2: 책 카드 표시
| 요소 | 데이터 | 처리 |
|------|--------|------|
| **제목, 저자** | `books_tagged.json` | 직접 표시 |
| **분야명** | `career_map[kdc].kdc_name` | 룩업 후 표시 |
| **AI 태그** | `student_tags` | 뱃지로 표시 |
| **관련 학과** | `career_map[kdc].departments[0:3]` | 카드 우측에 "관련 학과" 섹션 |
| **학과의 교과목** | `career_map[kdc].departments.subjects` | 마우스 호버 시 팝업 |
| **관련 진로** | `career_map[kdc].departments.careers` | "진로 연결" 섹션 |

**카드 레이아웃 예시**:
```
┌─────────────────────────────────┐
│ Love That Dog                   │
│ 샤론 크리치                      │
├─────────────────────────────────┤
│ 분야: 문학(800)                 │
│ 태그: #시쓰기 #감정표현         │
├─────────────────────────────────┤
│ 관련 학과 (상위 3개):          │
│ • 국어국문학과                  │
│   - 고전문학, 현대문학, 창작... │
│   진로: 국어교사, 작가          │
│ • 문예창작학과                  │
│   - 시창작, 소설창작, ...       │
│ • 문화콘텐츠학과                │
└─────────────────────────────────┘
```

**웹파일**: `book-card.html` + `js/app.js`

---

### 기능 3: "다른 시각으로 보기"
| 요소 | 데이터 | 처리 |
|------|--------|------|
| **연결 존재 확인** | `side_shelf_map.connections[kdc]` | 배열 있는지 확인 |
| **연결 선택** | 3개 중 1개 `Math.random()` | 새로고침할 때마다 바뀜 |
| **제시 문구** | `target.label` | "과학이 만드는 기술" |
| **설명** | `target.reason` | 호버 시 팝업 |
| **책 추천** | `books.filter(b => b.kdc==target_kdc && tags_match)` | 3권 랜덤 선택 |

**태그 매칭 로직**:
```javascript
let example_tags = target.example_tags; // ["응용과학", "바이오기술", ...]
let matching_books = books
  .filter(b => b.kdc === target.target_kdc)
  .filter(b => b.student_tags.some(tag => 
    example_tags.some(ex => tag.includes(ex) || ex.includes(tag))
  ));
// 매칭 안 되면 그냥 무작위 3권
```

**웹파일**: `js/app.js` (카드 우측에 "다른 시각으로 보기" 섹션)

---

### 기능 4: 개인 독서 분석
| 요소 | 데이터 | 처리 |
|------|--------|------|
| **읽은 책 저장** | 로컬스토리지 | `localStorage.myBooks = JSON.stringify([book_indices])` |
| **분야 비율** | `books[i].kdc` 그룹핑 | Chart.js 도넛 차트 |
| **태그 워드클라우드** | `books[i].student_tags` 수집 | Word Cloud 라이브러리 |
| **미탐색 분야** | KDC 전체 vs 읽은 것 | "과학 분야는 많고, 철학은 적습니다" |

**웹파일**: `my-shelf.html` + `js/analysis.js` (Chart.js)

---

### 기능 5: 진로 연결 정보
| 요소 | 데이터 | 처리 |
|------|--------|------|
| **관련 학과** | `career_map[kdc].departments[].name` | "물리학과, 천문학과, ..." |
| **배우는 과목** | `career_map[kdc].departments[].subjects` | "고전역학, 양자역학, ..." |
| **진로** | `career_map[kdc].departments[].careers` | "물리학연구원, 반도체기술자, ..." |
| **CareerNet 링크** | (수동 추가) | `https://www.career.go.kr/cnet/...` |

**표시 위치**: 기능 2 (책 카드) 내 "관련 학과" 섹션

---

## 데이터 가공 순서

### ✓ 완료된 것
1. `raw_books.json` 수집 (7,085권)
2. `kdc_tree.json` 생성
3. `career_map.json` 생성 (전국대학별학과정보표준데이터.csv 활용)
4. `side_shelf_map.json` 생성 (30개 연결)

### 진행 중
5. **`books_tagged.json` 완성** (Gemini Web에서 받은 데이터 병합)

### 아직 할 것
6. 웹 MVP 구현 (phase 3, 5~7일)
7. 분석 보고서 (phase 5)

---

## Gemini 처리 방식 결정

| 항목 | 선택지 A (Web UI) | 선택지 B (API) |
|------|-----------------|-----------------|
| **비용** | 무료 | $1.31 |
| **소요시간** | 2~3시간 (7회 복붙) | 5분 (자동) |
| **CI/CD 공유** | 불가 | ✓ GitHub Actions |
| **추천** | 시간 여유 있으면 | **친구 API 있으면** |

**최종 결정**:
- 친구가 API 구매 → **선택지 B** ($1.31, CI/CD 공유)
- 지금 당장 필요 → **선택지 A** (7회 배치)

