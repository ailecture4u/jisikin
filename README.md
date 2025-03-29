# 네이버 지식인 자동 답변 시스템

네이버 지식인에서 질문을 검색하고 GPT 기반의 자동 답변을 작성하여 게시하는 자동화 시스템입니다.

## 기능

- 네이버 지식인 질문 자동 검색
- 질문 내용 크롤링
- GPT 기반 자동 답변 생성
- 답변 자동 게시
- 오류 처리 및 로깅

## 설치 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd naver-kin-auto-answer
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. Playwright 브라우저 설치
```bash
playwright install
```

5. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가합니다:
```
OPENAI_API_KEY=your_api_key
NAVER_USERNAME=your_username
NAVER_PASSWORD=your_password
```

## 사용 방법

1. 설정 파일 수정
`config.py`에서 검색 키워드, 필터링 옵션 등을 설정합니다.

2. 프로그램 실행
```bash
python main.py
```

## 주의사항

- 네이버 지식인 이용약관을 준수해주세요.
- API 사용량과 비용을 고려하여 적절한 사용이 필요합니다.
- 자동화된 답변의 품질을 주기적으로 모니터링하세요.

## 라이선스

MIT License 