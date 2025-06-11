from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from config import llm

import json

@tool
def generate_assessment_answer(data):
    """지원자의 답변 평가"""
    class AssessmentResult(BaseModel):
        logicScore: int
        jobFitScore: int
        coreValueFitScore: int
        communicationScore: int
        averageScore: float

    parser = JsonOutputParser(pydantic_object=AssessmentResult)
    
    resume = data["resume"]
    jd = data["jd"]
    company = data["company"]
    answer = data["answer"]

    assessment_prompt = PromptTemplate(
        input_variables=["resume", "jd", "company_infos", "chat_history"],
        template="""
            역할:
            당신은 면접관입니다. 지원자의 답변을 듣고 다음 질문을 생성해야 합니다.
            지원자가 답변한 내용이 처음 질문에 적합한 답변인지 철저하게 판단하고, 그 판단에 의거해서 후속질문을 만들어야 한다.

            상황:
            당신이 보고있는 화면에는 지원자가 지원한 직무 JD, 지원자의 RESUME 등이 있는 상황입니다.
            이 면접자가 해당 직무의 담당자로 입사해서 충분한 역할을 하고, 회사와 함께 성장할 수 있는지 판단하기 위해 지원자를 검증해야합니다.

            직무 설명:
            {jd}

            자기소개서:
            {resume}

            회사 자료:
            {company}

            이전 답변 : 
            {answer}
            
            위 질문/답변 내용들을 바탕으로 
            현재 지원자가 다음 항목들에 대하여 얼마나 잘 답변했는지 평가해야 한다.
            평가 결과는 0~10점 사이의 점수로 표현해야 한다.
            평가 결과는 논리성, 직무적합성, 핵심가치 부합성, 커뮤니케이션 능력 4가지 항목에 대하여 평가해야 한다.
            평가 결과는 평균 점수도 함께 표현해야 한다.


            평가 결과는 JSON 형식으로 표현해야 한다.
            결과 예시 : {{
                "logicScore": 7,
                "jobFitScore": 6,
                "coreValueFitScore": 3,
                "communicationScore": 7,
                "averageScore": 5.6,
            }}
        """,
    )

    assessment_chain = assessment_prompt | llm | parser
    return assessment_chain