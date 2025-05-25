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


# 프롬프트 템플릿: 면접관 역할, 자소서/JD context 포함
QUESTION_PROMPT = """
당신은 면접관입니다. 다음 자소서와 JD를 기반으로 사용자에게 직무 관련 면접 질문을 하십시오.

[자소서]
{resume}

[JD]
{jd}

면접 질문 하나만 생성하세요:
"""

prompt = PromptTemplate(input_variables=["resume", "jd"], template=QUESTION_PROMPT)

# LLM 초기화
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model_name="gpt-4"
)


def get_interview_chain():
    logger.info("Starting interview chain initialization...")

    # 프롬프트 템플릿 (회사 자료 포함)
    prompt = PromptTemplate(
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
    logger.info("Prompt template created")

    # LLM 체인
    try:
        logger.info("Initializing ChatOpenAI...")
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model_name="gpt-4"
        )
        logger.info("ChatOpenAI initialized successfully")

        logger.info("Creating LLMChain...")
        chain = LLMChain(llm=llm, prompt=prompt, output_key="result")
        logger.info("LLMChain created successfully")

        return chain
    except Exception as e:
        logger.error(f"Error in chain creation: {str(e)}")
        raise


def get_followup_chain():
    """면접관이 지원자의 답변을 듣고 다음 질문을 생성하는 체인"""
    logger.info("Starting followup chain initialization...")

    # 프롬프트 템플릿
    prompt = PromptTemplate(
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

    # LLM 체인
    try:
        logger.info("Initializing ChatOpenAI...")
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model_name="gpt-4"
        )
        logger.info("ChatOpenAI initialized successfully")

        logger.info("Creating LLMChain...")
        chain = LLMChain(llm=llm, prompt=prompt, output_key="result")
        logger.info("LLMChain created successfully")

        return chain
    except Exception as e:
        logger.error(f"Error in chain creation: {str(e)}")
        raise
