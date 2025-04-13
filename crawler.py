from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import asyncio
from loguru import logger
from config import settings
import time

class NaverKinCrawler:
    def __init__(self):
        self.base_url = "https://kin.naver.com"
        self.search_url = f"{self.base_url}/search/list.naver"
        
    async def init_browser(self):
        """브라우저 초기화"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
    async def close(self):
        """브라우저 종료"""
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
        
    async def login(self):
        """네이버 로그인"""
        try:
            await self.page.goto("https://nid.naver.com/nidlogin.login")
            await self.page.fill("#id", settings.NAVER_USERNAME)
            await self.page.fill("#pw", settings.NAVER_PASSWORD)
            await self.page.click(".btn_login")
            await self.page.wait_for_load_state("networkidle")
            logger.info("네이버 로그인 성공")
        except Exception as e:
            logger.error(f"로그인 실패: {str(e)}")
            raise
            
    async def search_questions(self, keyword: str) -> List[Dict]:
        """키워드로 질문 검색"""
        questions = []
        try:
            search_url = f"{self.search_url}?query={keyword}&sort=0"
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            
            # 검색 결과 파싱
            soup = BeautifulSoup(await self.page.content(), "html.parser")
            question_items = soup.select(".search_list .search_item")
            
            for item in question_items[:settings.MAX_QUESTIONS_PER_KEYWORD]:
                try:
                    title_elem = item.select_one(".search_title")
                    if not title_elem:
                        continue
                        
                    question = {
                        "title": title_elem.get_text(strip=True),
                        "url": self.base_url + title_elem.get("href", ""),
                        "views": int(item.select_one(".search_count").get_text(strip=True).replace("조회수", "").replace(",", "")),
                        "answers": int(item.select_one(".search_answer").get_text(strip=True).replace("답변수", "").replace(",", ""))
                    }
                    
                    # 필터링 조건 적용
                    if (question["views"] >= settings.MIN_VIEWS and 
                        question["answers"] <= settings.MAX_ANSWERS):
                        questions.append(question)
                        
                except Exception as e:
                    logger.warning(f"질문 파싱 중 오류 발생: {str(e)}")
                    continue
                    
            logger.info(f"키워드 '{keyword}'로 {len(questions)}개의 질문 검색 완료")
            return questions
            
        except Exception as e:
            logger.error(f"질문 검색 중 오류 발생: {str(e)}")
            return []
            
    async def get_question_detail(self, url: str) -> Optional[Dict]:
        """질문 상세 내용 크롤링"""
        try:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            
            soup = BeautifulSoup(await self.page.content(), "html.parser")
            
            # 질문 제목
            title = soup.select_one(".title").get_text(strip=True)
            
            # 질문 내용
            content = soup.select_one(".question-content").get_text(strip=True)
            
            # 질문자 정보
            author = soup.select_one(".author").get_text(strip=True)
            
            # 작성일
            date = soup.select_one(".date").get_text(strip=True)
            
            return {
                "title": title,
                "content": content,
                "author": author,
                "date": date,
                "url": url
            }
            
        except Exception as e:
            logger.error(f"질문 상세 내용 크롤링 중 오류 발생: {str(e)}")
            return None
            
    async def post_answer(self, question_url: str, answer_content: str):
        """답변 작성 및 게시"""
        try:
            await self.page.goto(question_url)
            await self.page.wait_for_load_state("networkidle")
            
            # 답변 작성 영역 찾기
            answer_box = await self.page.query_selector(".answer_write")
            if not answer_box:
                logger.error("답변 작성 영역을 찾을 수 없습니다.")
                return False
                
            # 답변 내용 입력
            await answer_box.fill(".textarea", answer_content)
            
            # 답변 등록 버튼 클릭
            await self.page.click(".btn_submit")
            await self.page.wait_for_load_state("networkidle")
            
            logger.info("답변 게시 완료")
            return True
            
        except Exception as e:
            logger.error(f"답변 게시 중 오류 발생: {str(e)}")
            return False