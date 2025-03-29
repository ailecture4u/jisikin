from playwright.async_api import async_playwright
from typing import List, Dict, Optional
import asyncio
from loguru import logger
from config import settings
import time
import random
import openai

class NaverKinCrawler:
    def __init__(self):
        self.base_url = "https://kin.naver.com"
        # OpenAI API 설정
        openai.api_key = settings.OPENAI_API_KEY
        
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
            
    async def extract_question_content(self, page):
        """질문 페이지에서 질문 내용을 추출"""
        try:
            logger.info("질문 내용을 추출하고 있습니다...")
            
            # 질문 제목 추출
            title_element = await page.query_selector("h3.title")
            question_title = ""
            if title_element:
                question_title = await title_element.text_content()
                logger.info(f"질문 제목: {question_title}")
            else:
                logger.warning("질문 제목을 찾을 수 없습니다. 다른 선택자를 시도합니다.")
                # 다른 선택자도 시도
                alt_title_elements = [
                    await page.query_selector(".c-heading__title"),
                    await page.query_selector(".title_text"),
                    await page.query_selector("h3")
                ]
                
                for elem in alt_title_elements:
                    if elem:
                        question_title = await elem.text_content()
                        logger.info(f"대체 선택자로 질문 제목 찾음: {question_title}")
                        break
            
            # 질문 내용 추출
            content_element = await page.query_selector("div.c-heading__content")
            question_content = ""
            if content_element:
                question_content = await content_element.text_content()
                logger.info(f"질문 내용 일부: {question_content[:100]}...")
            else:
                logger.warning("질문 내용을 찾을 수 없습니다. 사용자가 제공한 XPath를 시도합니다.")
                
                # 사용자가 제공한 XPath 사용
                user_xpath = "/html/body/div[2]/div[3]/div[1]/div[1]/div[3]"
                user_content_element = await page.query_selector(f"xpath={user_xpath}")
                
                if user_content_element:
                    question_content = await user_content_element.text_content()
                    logger.info(f"사용자 제공 XPath로 질문 내용 찾음: {question_content[:100]}...")
                else:
                    logger.warning("사용자 제공 XPath로도 질문 내용을 찾을 수 없습니다. 다른 선택자를 시도합니다.")
                    # 다른 선택자도 시도
                    alt_content_elements = [
                        await page.query_selector(".question-content"),
                        await page.query_selector(".c-heading__detail"),
                        await page.query_selector(".content"),
                        await page.query_selector(".se-module-text")
                    ]
                    
                    for elem in alt_content_elements:
                        if elem:
                            question_content = await elem.text_content()
                            logger.info(f"대체 선택자로 질문 내용 찾음: {question_content[:100]}...")
                            break
            
            # 질문 카테고리 추출
            category_element = await page.query_selector("div.tag-list")
            question_category = ""
            if category_element:
                question_category = await category_element.text_content()
                logger.info(f"질문 카테고리: {question_category}")
            
            # 추출한 내용 조합
            full_question = f"제목: {question_title}\n\n카테고리: {question_category}\n\n내용: {question_content}"
            return full_question
            
        except Exception as e:
            logger.error(f"질문 내용 추출 중 오류 발생: {str(e)}")
            return "질문 내용을 추출하지 못했습니다."
            
    async def generate_answer_with_gpt(self, question_content):
        """ChatGPT를 사용하여 질문에 대한 답변 생성"""
        try:
            logger.info("ChatGPT로 답변 생성 중...")
            
            # ChatGPT 프롬프트 구성
            prompt = f"""다음은 네이버 지식인 질문입니다. 친절하고 도움이 되는 답변을 작성해주세요:

{question_content}

답변 작성 시 다음 규칙을 반드시 지켜주세요:
1. 마크다운 형식의 기호(#, *, _, - 등)를 사용하지 말 것
2. 줄바꿈은 한 번만 사용하고 필요한 경우에만 사용할 것
3. 간결하게 작성할 것
4. 포맷팅 없이 일반 텍스트로만 작성할 것

답변:"""
            
            # ChatGPT API 호출 (응답 속도 향상을 위한 설정 추가)
            response = await openai.ChatCompletion.acreate(
                model=settings.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "당신은 네이버 지식인에서 전문적이고 친절한 답변을 제공하는 도우미입니다. 마크다운 기호(#, *, _)를 사용하지 말고, 줄바꿈은 꼭 필요한 경우에만 한 번씩만 사용하세요. 빠르고 간결하게 답변하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                presence_penalty=0.3,  # 낮춰서 응답 속도 향상
                frequency_penalty=0.3  # 낮춰서 응답 속도 향상
            )
            
            # 생성된 답변 추출
            generated_answer = response.choices[0].message.content.strip()
            
            # 마크다운 기호 제거 및 줄바꿈 정리
            generated_answer = self.clean_markdown_format(generated_answer)
            
            # 답변 마지막에 채택 부탁 문구 추가
            generated_answer = generated_answer + "\n\n읽어주셔서 감사하며 한 번 채택 부탁드려요!"
            
            logger.info(f"생성된 답변 일부: {generated_answer[:100]}...")
            
            return generated_answer
            
        except Exception as e:
            logger.error(f"ChatGPT 답변 생성 중 오류 발생: {str(e)}")
            return "죄송합니다. 답변을 생성하는 과정에서 오류가 발생했습니다."  # 오류 발생 시 기본 오류 메시지 반환
            
    def clean_markdown_format(self, text):
        """마크다운 형식 제거 및 줄바꿈 정리"""
        import re
        
        # 마크다운 기호 제거
        # 제목 기호 제거 (## 등)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # 볼드체, 이탤릭체 기호 제거 (**, * 등)
        text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)
        # 언더라인 기호 제거 (_ 등)
        text = re.sub(r'_{1,2}(.*?)_{1,2}', r'\1', text)
        # 리스트 기호 제거 (-, *, 1. 등)
        text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # 연속된 공백 줄이기
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
            
    async def answer_questions(self, answer_text):
        """검색 결과의 질문들을 클릭하고 답변하기"""
        try:
            logger.info("검색 결과의 질문들에 답변하기 시작")
            
            # 검색 결과 URL 저장
            search_results_url = self.page.url
            
            # 검색 결과 페이지에서 li[1]부터 li[10]까지의 링크 클릭 및 답변
            for i in range(1, 11):
                try:
                    # 이전 버전에서는 여기서 현재 검색 결과 페이지로 다시 이동했지만,
                    # 새 탭 처리 로직으로 인해 이제 필요 없음
                    
                    # i번째 질문 링크 찾기
                    question_xpath = f"//html/body/div[2]/div[3]/div/div/div[2]/div/div[3]/ul/li[{i}]/dl/dt/a"
                    logger.info(f"{i}번째 질문을 찾고 있습니다...")
                    
                    # 해당 질문이 페이지에 존재하는지 확인
                    question_link = await self.page.query_selector(question_xpath)
                    if not question_link:
                        logger.warning(f"{i}번째 질문을 찾을 수 없습니다. 다음 질문으로 넘어갑니다.")
                        continue
                    
                    # 질문 제목 가져오기
                    question_title = await question_link.text_content()
                    logger.info(f"{i}번째 질문 제목: {question_title}")
                    
                    # 질문 링크 클릭
                    logger.info(f"{i}번째 질문 링크를 클릭합니다...")
                    
                    # 새 탭이 열리는 것을 감지하기 위한 이벤트 리스너 설정
                    async with self.context.expect_page() as new_page_info:
                        await question_link.click()
                    
                    # 새로 열린 탭 가져오기
                    question_page = await new_page_info.value
                    
                    # 새 탭으로 전환
                    await question_page.bring_to_front()
                    logger.info("새 탭으로 전환했습니다.")
                    
                    # 질문 상세 페이지 로딩 대기
                    await question_page.wait_for_load_state("networkidle")
                    logger.info(f"{i}번째 질문 상세 페이지 로딩 완료")
                    
                    # 질문 내용 추출
                    question_content = await self.extract_question_content(question_page)
                    
                    # ChatGPT를 사용하여 답변 생성
                    current_answer = await self.generate_answer_with_gpt(question_content)
                    logger.info("AI가 답변을 생성했습니다")
                    
                    # 답변하기 버튼 찾기
                    logger.info("답변하기 버튼을 찾고 있습니다...")
                    # XPath 선택자 형식 수정
                    answer_button = await question_page.query_selector("xpath=//div[2]/div[3]/div[1]/div[4]/div/div/div/div[3]/button")
                    
                    if not answer_button:
                        # 다른 형태의 답변하기 버튼도 시도
                        alternative_button = await question_page.query_selector("button:has-text('답변하기')")
                        if alternative_button:
                            answer_button = alternative_button
                        else:
                            logger.warning(f"{i}번째 질문에 대한 답변하기 버튼을 찾을 수 없습니다.")
                            logger.info("답변하기 버튼을 찾지 못했습니다. 사용자가 직접 확인할 수 있도록 잠시 멈춥니다.")
                            logger.info("직접 답변하기 버튼을 찾아보신 후, 계속하려면 엔터 키를 누르세요...")
                            input("프로세스를 계속하려면 엔터 키를 누르세요...")
                            
                            # 사용자가 직접 답변하기를 눌렀는지 확인
                            logger.info("사용자 입력 후 페이지 상태를 다시 확인합니다...")
                            
                            # 페이지가 변경되었을 수 있으므로 로딩 상태 대기
                            await question_page.wait_for_load_state("networkidle")
                            
                            # 답변 폼이 열렸는지 확인 (답변 에디터 또는 텍스트 영역을 찾아본다)
                            editor_iframe = await question_page.query_selector("iframe.se2_input_area")
                            text_area = await question_page.query_selector("textarea.txtArea")
                            
                            if not editor_iframe and not text_area:
                                logger.warning("여전히 답변 입력 폼을 찾을 수 없습니다. 다음 질문으로 넘어갑니다.")
                                await question_page.close()
                                continue
                            else:
                                logger.info("답변 입력 폼이 감지되었습니다. 계속 진행합니다.")
                                # 답변 버튼을 찾았거나 사용자가 이미 클릭했다고 가정하고 계속 진행
                    
                    # 답변하기 버튼 클릭
                    logger.info("답변하기 버튼을 클릭합니다...")
                    await answer_button.click()
                    
                    # 답변 입력 폼 로딩 대기
                    await question_page.wait_for_load_state("networkidle")
                    logger.info("키보드 직접 입력으로 답변 작성을 시도합니다...")
                    
                    # 답변 폼이 완전히 로드될 때까지 충분히 대기
                    await asyncio.sleep(2.0)
                    
                    # 한 글자씩 천천히 타이핑하듯이 입력
                    try:
                        # 먼저 에디터 영역을 선택자로 찾아보기
                        editor_area = await question_page.query_selector("div.se-component-content")
                        
                        if editor_area:
                            # 에디터 영역을 찾았다면 해당 요소가 보이도록 스크롤
                            logger.info("에디터 영역을 찾았습니다. 해당 영역으로 스크롤합니다.")
                            await editor_area.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            # 에디터 영역 클릭
                            await editor_area.click()
                        else:
                            # 에디터를 찾지 못했다면 대체 방법으로 스크롤 후 클릭
                            logger.info("에디터 영역을 찾지 못했습니다. 페이지 중앙을 클릭합니다.")
                            # 스크롤 위치 안정화
                            await question_page.evaluate("window.scrollTo(0, 400)")
                            await asyncio.sleep(1.0)
                            # 입력 가능한 영역 클릭을 시도 (에디터가 있을 가능성이 높은 중앙 영역)
                            await question_page.mouse.click(640, 400)
                        
                        await asyncio.sleep(1.0)
                        
                        # 답변에서 불필요한 엔터와 기호 제거 (추가 확인)
                        clean_answer = current_answer.replace('\n\n', '\n')
                        
                        # 한 글자씩 천천히 입력
                        for char in clean_answer:
                            await question_page.keyboard.type(char, delay=random.randint(10, 30))
                            # 가끔 잠시 멈추기 (실제 사람이 생각하는 것처럼)
                            if random.random() < 0.1:
                                await asyncio.sleep(random.uniform(0.1, 0.3))
                            
                            # '\n'을 만나면 Enter 키 입력
                            if char == '\n':
                                await question_page.keyboard.press("Enter")
                                await asyncio.sleep(0.1)
                        
                        logger.info("키보드 입력으로 답변 작성 완료")
                    except Exception as typing_error:
                        logger.error(f"키보드 입력 중 오류 발생: {str(typing_error)}")
                        logger.info("사용자의 수동 개입이 필요합니다.")
                        logger.info("직접 답변을 입력해주신 후, 계속하려면 엔터 키를 누르세요...")
                        input("직접 입력 후 엔터 키를 누르세요...")
                    
                    # 에디터 프레임 찾기 로직과 XPath 검색 로직 제거 (단순화)
                    
                    logger.info("답변 입력 완료, 등록 버튼을 찾고 있습니다...")
                    
                    # 등록 버튼 찾아서 클릭 (사용자가 제공한 XPath 사용)
                    submit_xpath = "/html/body/div[2]/div[3]/div[1]/div[4]/div/div[1]/div/div/div[3]/button"
                    submit_button = await question_page.query_selector(f"xpath={submit_xpath}")
                    
                    if not submit_button:
                        # 기존 방법으로 등록 버튼 찾기 시도
                        submit_button = await question_page.query_selector("//a[contains(., '등록')]")
                        if not submit_button:
                            submit_button = await question_page.query_selector("button:has-text('등록')")
                        
                    if submit_button:
                        logger.info("답변 등록 버튼을 클릭합니다...")
                        await submit_button.click()
                        await question_page.wait_for_load_state("networkidle")
                        logger.info(f"{i}번째 질문에 답변 완료")
                        
                        # 봇 감지를 위한 인증번호 입력 시간 제공 (30초 대기)
                        logger.info("인증번호 입력이 필요한 경우를 위해 30초간 대기합니다...")
                        await asyncio.sleep(30)
                        logger.info("대기 시간이 끝났습니다. 계속 진행합니다.")
                    else:
                        logger.warning("답변 등록 버튼을 찾을 수 없습니다.")
                        logger.info("등록 버튼을 찾지 못했습니다. 사용자가 직접 확인할 수 있도록 잠시 멈춥니다.")
                        logger.info("직접 등록 버튼을 찾아보신 후, 계속하려면 엔터 키를 누르세요...")
                        input("프로세스를 계속하려면 엔터 키를 누르세요...")
                        
                        # 사용자가 직접 등록했는지 확인하기 위해 잠시 대기
                        logger.info("사용자 입력 후 페이지 상태를 다시 확인합니다...")
                        await question_page.wait_for_load_state("networkidle")
                        logger.info("사용자 확인 후 계속 진행합니다")
                    
                    # 질문 탭 닫기
                    await question_page.close()
                    logger.info(f"{i}번째 질문 탭을 닫았습니다.")
                    
                    # 원래 검색 결과 탭으로 돌아가기
                    await self.page.bring_to_front()
                
                except Exception as e:
                    logger.error(f"{i}번째 질문 답변 중 오류 발생: {str(e)}")
                    logger.info("오류가 발생했습니다. 사용자가 직접 확인할 수 있도록 잠시 멈춥니다.")
                    logger.info("문제를 확인하신 후, 계속하려면 엔터 키를 누르세요...")
                    
                    try:
                        # 아직 페이지가 열려 있는지 확인
                        if 'question_page' in locals() and question_page.is_closed() == False:
                            input("프로세스를 계속하려면 엔터 키를 누르세요...")
                            
                            # 질문 탭 닫기 
                            await question_page.close()
                            logger.info(f"{i}번째 질문 탭을 닫았습니다.")
                            
                            # 원래 검색 결과 탭으로 돌아가기
                            await self.page.bring_to_front()
                    except Exception as inner_e:
                        logger.error(f"오류 처리 중 추가 예외 발생: {str(inner_e)}")
                    
                    continue
            
            logger.info("모든 질문에 대한 답변 작업 완료")
            return True
            
        except Exception as e:
            logger.error(f"답변 과정 중 오류 발생: {str(e)}")
            return False 