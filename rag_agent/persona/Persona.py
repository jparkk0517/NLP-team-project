from uuid import uuid4
from langchain_core.output_parsers import (
    StrOutputParser,
)
from typing import Literal, Optional

from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import os


# .env 파일 로드
load_dotenv()
PersonaType = Literal["developer", "designer", "product_manager", "other"]

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model_name="gpt-4o"
)


class Persona(BaseModel):
    """
    면접 에이전트의 Persona
    """

    id: str
    type: PersonaType
    name: str
    interests: Optional[list[str]] = None
    communication_style: Optional[str] = None
    persona_template: PromptTemplate = None

    def __init__(
        self,
        type: PersonaType,
        name: str,
        interests: Optional[list[str]] = None,
        communication_style: Optional[str] = None,
    ):
        self.id = str(uuid4().hex[:8])
        self.type = type
        self.name = name
        self.interests = interests
        self.communication_style = communication_style
        self.pesrona_prompt = PromptTemplate(
            template=f"""
            [역할]
            당신은 {type}의 면접관 {name}입니다.
            당신은 면접관으로 면접장에 위치해 있으며 당신의 앞에는 지원자가 있습니다.
            당신은 {communication_style} 방식으로 지원자와 대화합니다.
            당신은 평소 {", ".join([interest for interest in interests])}에 관심이 있습니다.
            """,
        )

    def get_base_prompt(self):
        return self.pesrona_prompt

    def get_persona_info(self):
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "interests": self.interests,
            "communication_style": self.communication_style,
        }

    def generate_question(self):
        question_prompt = PromptTemplate(
            input_variables=["resume", "jd", "company_infos"],
            template="""
            [직무설명]
            {jd}
            
            [이력서]
            {resume}
            
            [회사 자료]
            {company_infos}
            
            [질문]
            지원자의 자기소개서를 평가하고 있습니다.
            """,
        )
        return self.get_base_prompt() | question_prompt | llm | StrOutputParser()

    def generate_model_answer(self):
        answer_prompt = PromptTemplate(
            input_variables=[
                "resume",
                "jd",
                "company_infos",
                "question",
            ],
            template="""
            [환경]

            [상황]
            
            """,
        )
        return self.get_base_prompt() | answer_prompt | llm | StrOutputParser()
