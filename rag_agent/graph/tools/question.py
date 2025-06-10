from langchain_core.tools import tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from config import llm

import json

@tool
def generate_question_reasoning(data):
    """Resumes, Job Descriptions, and Company Info를 기반으로 질문 이유(Reasoning)를 도출"""

    resume = data["resume"]
    jd = data["jd"]
    company = data["company"]
    
    reasoning_prompt = PromptTemplate.from_template(
        """
        다음은 한 지원자의 자소서, JD(직무기술서), 회사 정보입니다:

        자소서:
        {resume}

        JD:
        {jd}

        회사 정보:
        {company}

        이 정보를 바탕으로, 아래 내용을 고려하여 면접 질문을 만들기 위한 Reasoning을 작성하세요:
        1. 회사 인재상에 부합하는 성격/역량/행동을 자소서에서 얼마나 확인할 수 있는가?
        2. JD에서 요구하는 자격요건, 기술, 경험과 자소서가 잘 부합하는가?
        3. 부족하거나 확인이 필요한 점은 무엇인가?

        [출력 예시]
        - 협업 역량이 회사 인재상에서 중요하지만 자소서에 구체적인 협업 경험이 언급되어 있지 않음.
        - JD에서 강조한 데이터 분석 경험이 자소서에 일부 존재하나 프로젝트 구체성 부족.
        """
    )
    
    chain = reasoning_prompt | llm | StrOutputParser()
    return chain.invoke({
        "resume": resume,
        "jd": jd,
        "company": company
    })


@tool
def generate_question_acting(reasoning):
    """Reasoning에 기반하여 실제 면접 질문을 생성"""
    acting_prompt = PromptTemplate.from_template(
        """
        다음은 면접 질문을 만들기 위한 Reasoning 리스트 입니다:

        {reasoning}

        이 정보를 바탕으로, 적절한 면접 질문 1개를 출력하세요.
        
        [예시 출력]
        협업 경험 중 가장 도전적이었던 상황은 무엇이었나요?
        """
    )
    
    chain = acting_prompt | llm | StrOutputParser()
    return chain.invoke({"reasoning": reasoning})