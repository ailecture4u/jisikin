from playwright.async_api import async_playwright
from typing import List, Dict, Optional
import asyncio
from loguru import logger
from config import settings
import time
import random

class NaverKinCrawler:
    def __init__(self):
        self.base_url = "https://kin.naver.com"
        
    async def init_browser(self):
        """브라우저 초기화"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(viewport={"width": 1280, "height": 800})
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
            logger.info("로그인 페이지로 이동했습니다. 직접 로그인해주세요.")
            
            # 사용자에게 로그인 완료 후 Enter 키를 누르도록 안내
            logger.info("로그인을 완료한 후 터미널에서 Enter 키를 눌러주세요...")
            input("로그인 완료 후 Enter 키를 눌러주세요...")
            
            # 로그인 완료 후 네트워크 요청이 안정화될 때까지 대기
            await self.page.wait_for_load_state("networkidle")
            logger.info("로그인 프로세스 완료")
            
            # 로그인 후 네이버 지식인 메인 페이지로 이동
            logger.info("네이버 지식인 메인 페이지로 이동합니다...")
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state("networkidle")
            logger.info("네이버 지식인 메인 페이지로 이동 완료")
            
        except Exception as e:
            logger.error(f"로그인 과정 중 오류 발생: {str(e)}")
            raise
            
    async def human_like_typing(self, element, text):
        """사람처럼 자연스럽게 타이핑하는 함수"""
        # 기존 텍스트 지우기
        await element.fill("")
        
        # 한 글자씩 타이핑
        for char in text:
            await element.type(char, delay=random.randint(50, 150))
            # 가끔 잠시 멈추기 (실제 사람이 생각하는 것처럼)
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
    async def search_keyword(self, keyword):
        """키워드 검색"""
        try:
            logger.info(f"키워드 검색을 시작합니다: {keyword}")
            
            # XPath로 검색창 찾기
            search_input = await self.page.wait_for_selector("//html/body/div[2]/div[2]/div[2]/div/div[1]/div/form/fieldset/div/input")
            
            if not search_input:
                logger.error("검색창을 찾을 수 없습니다. XPath가 변경되었을 수 있습니다.")
                return False
                
            # 사람처럼 자연스럽게 타이핑
            await self.human_like_typing(search_input, keyword)
            
            # 잠시 대기 (검색어 입력 후 잠시 생각하는 것처럼)
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # 검색 버튼 XPath (수정된 XPath 사용)
            search_button = await self.page.wait_for_selector("//html/body/div[2]/div[2]/div[2]/div/div[1]/div/form/fieldset/div/a[2]")
            
            if not search_button:
                logger.error("검색 버튼을 찾을 수 없습니다.")
                return False
                
            # 검색 버튼 클릭
            logger.info("검색 버튼을 클릭합니다...")
            await search_button.click()
            
            # 검색 결과 페이지 로딩 대기
            await self.page.wait_for_load_state("networkidle")
            logger.info(f"'{keyword}' 검색 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"키워드 검색 중 오류 발생: {str(e)}")
            return False 