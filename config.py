from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")#env에서 들어옴 
    
    # 검색 설정
    SEARCH_KEYWORDS: List[str] = [
        "파이썬",
        "프로그래밍",
        "코딩",
        "개발"
    ]
    
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