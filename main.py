import asyncio
from loguru import logger
import sys
from config import settings
from crawler import NaverKinCrawler
from answer_generator import AnswerGenerator

# 로깅 설정
logger.remove()
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    settings.LOG_FILE,
    rotation="1 day",
    retention="7 days",
    level=settings.LOG_LEVEL
)

async def main():
    """메인 실행 함수"""
    try:
        # 크롤러 초기화
        crawler = NaverKinCrawler()
        await crawler.init_browser()
        
        # 답변 생성기 초기화
        answer_generator = AnswerGenerator()
        
        # 로그인
        await crawler.login()
        
        # 각 키워드별로 질문 검색 및 답변
        for keyword in settings.SEARCH_KEYWORDS:
            logger.info(f"키워드 '{keyword}' 검색 시작")
            
            # 질문 검색
            questions = await crawler.search_questions(keyword)
            
            for question in questions:
                try:
                    # 질문 상세 내용 가져오기
                    question_detail = await crawler.get_question_detail(question["url"])
                    if not question_detail:
                        continue
                        
                    logger.info(f"질문 처리 중: {question_detail['title']}")
                    
                    # 답변 생성
                    answer = await answer_generator.generate_answer(
                        question_detail["title"],
                        question_detail["content"]
                    )
                    
                    # 답변 포맷팅
                    formatted_answer = answer_generator.format_answer(answer)
                    
                    # 답변 게시
                    success = await crawler.post_answer(
                        question["url"],
                        formatted_answer
                    )
                    
                    if success:
                        logger.info(f"답변 게시 완료: {question_detail['title']}")
                    else:
                        logger.error(f"답변 게시 실패: {question_detail['title']}")
                        
                    # 딜레이 추가
                    await asyncio.sleep(settings.CRAWLING_DELAY)
                    
                except Exception as e:
                    logger.error(f"질문 처리 중 오류 발생: {str(e)}")
                    continue
                    
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {str(e)}")
    finally:
        # 브라우저 종료
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(main())