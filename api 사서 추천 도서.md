# 사서 추천 도서 API 수집 방법

## 데이터 출처
**국립어린이청소년도서관 사서 추천 도서**
- 공공데이터포털: https://www.data.go.kr
- 검색어: "국립어린이청소년도서관 사서추천도서"
- 제공 정보: 도서명, 저자, 출판사, 발행연도, KDC 분류번호, 도서 소개, 대상 연령

## API 키 발급 절차
1. https://www.data.go.kr 회원가입 및 로그인
2. "국립어린이청소년도서관 사서추천도서 목록" 검색
3. [활용신청] 버튼 클릭
4. 활용 목적 입력 (예: 교육 데이터 분석 연구)
5. 승인 후 마이페이지 → 개발계정 → 일반 인증키(디코딩) 복사

## 스크립트 실행 방법

```bash
# 1. API 키를 scripts/fetch_books_api.py에 입력
# API_KEY = "발급받은 인증키" 로 수정

# 2. 실행
python scripts/fetch_books_api.py
# → data/raw_books.json 생성

# 3. AI 태그 생성 (ANTHROPIC_API_KEY 환경변수 필요)
python scripts/generate_tags.py
# → data/books_tagged.json 생성
```

## 현재 상태
- `data/raw_books_sample.json`: 테스트용 샘플 10권 (직접 작성)
- `data/books_tagged.json`: 샘플 10권 AI 태그 완성본 (웹 MVP 테스트용)
- 실제 API 수집 후 books_tagged.json을 전체 데이터로 교체 예정

## API 응답 구조 (예상)
```json
{
  "response": {
    "body": {
      "totalCount": 1500,
      "items": {
        "item": [
          {
            "bookNm": "도서명",
            "authrNm": "저자명",
            "pblcatnPlc": "출판사",
            "pblcatnYr": "발행연도",
            "kdcNm": "KDC 분류",
            "bkIntrcn": "도서 소개",
            "lsnrAge": "대상 연령",
            "isbn": "ISBN"
          }
        ]
      }
    }
  }
}
```
