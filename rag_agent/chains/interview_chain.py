from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import logging

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# LLM 초기화
logger.info("Starting interview chain initialization...")
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model_name="gpt-4o"
)


def get_interview_chain():
    interview_prompt = PromptTemplate(
        input_variables=["resume", "jd", "company_infos"],
        template="""
            역할:
            당신은 면접관입니다. 지원자의 답변을 듣고 다음 질문을 생성해야 합니다.
            지원자가 답변한 내용이 처음 질의에 적합한 답변인지 철저하게 판단하고, 그 판단에 의거해서 후속질문을 만들어야 한다.

            상황:
            당신이 보고있는 화면에는 지원자가 지원한 직무 JD, 지원자의 RESUME 등이 있는 상황입니다.
            이 면접자가 해당 직무의 담당자로 입사해서 충분한 역할을 하고, 회사와 함께 성장할 수 있는지 판단하기 위해 지원자를 검증해야합니다.
            

            회사 자료:
            {company_infos}

            chain of thought:
            지원자를 검증하기 위해 이력서,JD를 파악해서 질문을 생성/응답 평가를 해야한다.
            아래 제시되는 이력서, 직무를 기반으로 면접질문을 이전에 제시하였고, 당신은 이 딥변을 듣고 이 질문에 대하여 followup하는 꼬리질문을 생성해야 한다.
            꼬리질문은 이 기업이 지원자에게 검증하고자 하는 핵심적인 포인트를 파악하기위한 목적이다.
            꼬리질문은 반드시 지원자의 답변에 대한 후속질문이어야 한다.


            이력서:
            {resume}

            직무 설명:
            {jd}
            
            질문을 하나만 생성한다:
            """,
    )

    interview_chain = LLMChain(llm=llm, prompt=interview_prompt, output_key="result")
    return interview_chain


def get_followup_chain():
    followup_prompt = PromptTemplate(
        input_variables=["resume", "jd", "company_infos", "question", "user_answer"],
        template="""
            역할:
            당신은 면접관입니다. 지원자의 답변을 듣고 다음 질문을 생성해야 합니다.
            지원자가 답변한 내용이 처음 질의에 적합한 답변인지 철저하게 판단하고, 그 판단에 의거해서 후속질문을 만들어야 한다.

            상황:
            당신이 보고있는 화면에는 지원자가 지원한 직무 JD, 지원자의 RESUME 등이 있는 상황입니다.
            이 면접자가 해당 직무의 담당자로 입사해서 충분한 역할을 하고, 회사와 함께 성장할 수 있는지 판단하기 위해 지원자를 검증해야합니다.
            

            회사 자료:
            {company_infos}

            chain of thought:
            지원자를 검증하기 위해 이력서,JD를 파악해서 질문을 생성/응답 평가를 해야한다.
            아래 제시되는 이력서, 직무를 기반으로 면접질문을 이전에 제시하였고, 당신은 이 딥변을 듣고 이 질문에 대하여 followup하는 꼬리질문을 생성해야 한다.
            꼬리질문은 이 기업이 지원자에게 검증하고자 하는 핵심적인 포인트를 파악하기위한 목적이다.
            꼬리질문은 반드시 지원자의 답변에 대한 후속질문이어야 한다.


            이력서:
            {resume}

            직무 설명:
            {jd}
            
            이전 질문/답변 쌍들:
            {prev_question_answer_pairs}

            답변은 지원자가 이전에 했던 답변을 요약하고, 그 요약 이후 후속질문을 생성한다.
            """,
    )

    followup_chain = LLMChain(llm=llm, prompt=followup_prompt, output_key="result")
    return followup_chain


def get_evaluate_chain():
    evaluate_prompt = PromptTemplate(
        input_variables=["resume", "jd", "company_infos", "prev_question_answer_pairs"],
        template="""
            역할:
            당신은 면접관입니다. 지원자의 답변을 듣고 다음 질문을 생성해야 합니다.
            지원자가 답변한 내용이 처음 질문에 적합한 답변인지 철저하게 판단하고, 그 판단에 의거해서 후속질문을 만들어야 한다.

            상황:
            당신이 보고있는 화면에는 지원자가 지원한 직무 JD, 지원자의 RESUME 등이 있는 상황입니다.
            이 면접자가 해당 직무의 담당자로 입사해서 충분한 역할을 하고, 회사와 함께 성장할 수 있는지 판단하기 위해 지원자를 검증해야합니다.

            직무 설명:
            {jd}

            이력서:
            {resume}

            회사 자료:
            {company_infos}

            이전 질문/답변 : 
            {prev_question_answer_pairs}
            
            답변 평가:
            답변이 처음 질문에 적합한 답변인지 철저하게 판단해야 한다.
        """,
    )

    evaluate_chain = LLMChain(llm=llm, prompt=evaluate_prompt, output_key="result")
    return evaluate_chain


def get_model_answer_chain():
    model_answer_prompt = PromptTemplate(
        input_variables=["resume", "jd", "company_infos", "question"],
        template="""
            역할:
            당신은 면접관입니다. 지원자의 답변을 듣고 다음 질문을 생성해야 합니다.
            지원자가 답변한 내용이 처음 질문에 적합한 답변인지 철저하게 판단하고, 그 판단에 의거해서 후속질문을 만들어야 한다.

            상황:
            당신이 보고있는 화면에는 지원자가 지원한 직무 JD, 지원자의 RESUME 등이 있는 상황입니다.
            이 면접자가 해당 직무의 담당자로 입사해서 충분한 역할을 하고, 회사와 함께 성장할 수 있는지 판단하기 위해 지원자를 검증해야합니다.

            회사 자료:
            {company_infos}

            직무 설명:
            {jd}

            이력서:
            {resume}

            질문:
            {question}

            모델 답변:
            위 상황에서 지원자가 주어진 질문에 대한 최선의 답변을 생성해야 한다.
            답변은 한글로 생성해야 한다.
        """,
    )

    model_answer_chain = LLMChain(
        llm=llm, prompt=model_answer_prompt, output_key="result"
    )
    return model_answer_chain


def get_assessment_chain():
    class AssessmentResult(BaseModel):
        logicScore: int
        jobFitScore: int
        coreValueFitScore: int
        communicationScore: int
        averageScore: float

    parser = JsonOutputParser(pydantic_object=AssessmentResult)

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

            이력서:
            {resume}

            회사 자료:
            {company_infos}

            이전 질문/답변 : 
            {chat_history}
            
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
    # LLMChain(
    #     llm=llm, prompt=assessment_prompt, output_key="result", parser=parser
    # )
    return assessment_chain
