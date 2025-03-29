import openai
import json
from typing import List
from loguru import logger
from config import settings
from pydantic import BaseModel, Field

class Answer(BaseModel):
    content: str
    references: List[str] = []

class AnswerGenerator:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        
    async def generate_answer(self, title: str, content: str) -> Answer:
        """질문에 대한 답변 생성"""
        try:
            # 프롬프트 생성
            system_prompt = """당신은 네이버 지식인의 전문가 답변자입니다.
            다음 가이드라인을 따라 답변을 생성해주세요:
            1. 정확하고 전문적인 정보를 제공하세요.
            2. 이해하기 쉽게 설명하세요.
            3. 필요한 경우 예시를 들어 설명하세요.
            4. 참고할 수 있는 자료나 링크를 포함하세요.
            5. 공손하고 친절한 톤을 유지하세요.
            6. 답변은 500자 이상으로 작성하세요.
            
            답변은 반드시 JSON 형식으로 반환하세요: {"content": "답변 내용", "references": ["참고자료1", "참고자료2"]}
            """
            
            user_prompt = f"""질문 제목: {title}
            질문 내용: {content}
            
            위 질문에 대한 답변을 생성해주세요."""
            
            # OpenAI API 호출
            response = openai.ChatCompletion.create(
                model=settings.GPT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            
            # 응답 파싱
            result = response.choices[0].message.content.strip()
            
            try:
                # JSON 형식 파싱
                answer_data = json.loads(result)
                answer = Answer(
                    content=answer_data.get("content", ""),
                    references=answer_data.get("references", [])
                )
            except json.JSONDecodeError:
                # JSON 파싱 실패시 전체 텍스트를 content로 사용
                logger.warning("JSON 파싱 실패, 전체 텍스트를 답변으로 사용합니다.")
                answer = Answer(content=result)
            
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