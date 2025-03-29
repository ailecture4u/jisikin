import asyncio
from loguru import logger
import sys
from config import settings
from crawler import NaverKinCrawler

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
        
        # 로그인
        await crawler.login()
        
        # 로그인 후 네이버 지식인 페이지에서 작업을 수행할 수 있습니다.
        logger.info("네이버 지식인 로그인 완료. 화면을 확인하세요.")
        
        # 사용자로부터 검색어 입력 받기
        search_keyword = input("검색어를 입력하세요: ")
        logger.info(f"입력한 검색어: {search_keyword}")
        
        # 검색 수행
        search_result = await crawler.search_keyword(search_keyword)
        
        if search_result:
            logger.info("검색이 완료되었습니다. 검색 결과 화면을 확인하세요.")
        else:
            logger.error("검색 과정에서 문제가 발생했습니다.")
        
        # 프로그램 종료 전 대기
        logger.info("브라우저 창을 유지합니다. 종료하려면 터미널에서 엔터 키를 누르세요...")
        input("프로그램을 종료하려면 엔터 키를 누르세요...")
                    
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {str(e)}")
    finally:
        # 브라우저 종료
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(main()) 