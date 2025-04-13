from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from loguru import logger
from config import settings

class Answer(BaseModel):
    content: str = Field(description="생성된 답변 내용")
    references: List[str] = Field(description="참고한 자료나 링크 목록")

class AnswerGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=settings.GPT_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY
        )
        self.parser = PydanticOutputParser(pydantic_object=Answer)
        
        # 답변 생성을 위한 프롬프트 템플릿
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """당신은 네이버 지식인의 전문가 답변자입니다.
            다음 가이드라인을 따라 답변을 생성해주세요:
            1. 정확하고 전문적인 정보를 제공하세요.
            2. 이해하기 쉽게 설명하세요.
            3. 필요한 경우 예시를 들어 설명하세요.
            4. 참고할 수 있는 자료나 링크를 포함하세요.
            5. 공손하고 친절한 톤을 유지하세요.
            6. 답변은 500자 이상으로 작성하세요.
            
            {format_instructions}"""),
            ("human", """질문 제목: {title}
            질문 내용: {content}
            
            위 질문에 대한 답변을 생성해주세요.""")
        ])
        
    async def generate_answer(self, title: str, content: str) -> Answer:
        """질문에 대한 답변 생성"""
        try:
            # 프롬프트 생성
            prompt = self.prompt_template.format_messages(
                title=title,
                content=content,
                format_instructions=self.parser.get_format_instructions()
            )
            
            # GPT 모델로 답변 생성
            response = await self.llm.ainvoke(prompt)
            
            # 응답 파싱
            answer = self.parser.parse(response.content)
            
            logger.info("답변 생성 완료")
            return answer
            
        except Exception as e:
            logger.error(f"답변 생성 중 오류 발생: {str(e)}")
            raise
            
    def format_answer(self, answer: Answer) -> str:
        """답변 포맷팅"""
        formatted_answer = answer.content + "\n\n"
        
        if answer.references:
            formatted_answer += "참고 자료:\n"
            for ref in answer.references:
                formatted_answer += f"- {ref}\n"
                
        return formatted_answer