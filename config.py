from pydantic import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # 네이버 계정 설정
    NAVER_USERNAME: str = os.getenv("NAVER_USERNAME", "")
    NAVER_PASSWORD: str = os.getenv("NAVER_PASSWORD", "")
    
    # 검색 설정
    SEARCH_KEYWORDS: List[str] = [
        "파이썬",
        "프로그래밍",
        "코딩",
        "개발"
    ]
    
    # 필터링 설정
    MIN_VIEWS: int = 100
    MAX_ANSWERS: int = 0  # 0은 미답변 질문만
    
    # GPT 설정
    GPT_MODEL: str = "gpt-4-turbo-preview"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # 크롤링 설정
    MAX_QUESTIONS_PER_KEYWORD: int = 10
    CRAWLING_DELAY: float = 2.0  # 초
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "naver_kin_auto_answer.log"

settings = Settings()