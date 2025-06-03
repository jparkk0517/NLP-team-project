from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# from .prompt_templates import classify_prompt, reasoning_prompt, acting_prompt
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_core.output_parsers import (
    StrOutputParser,
    CommaSeparatedListOutputParser,
    JsonOutputParser,
)
from typing import Callable, Literal, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from uuid import uuid4

import os
import logging
import shutil
import json

# PDF/DOCX 파싱
import PyPDF2
import docx

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


@tool
def classify_input(input):
    """입력이 자소서인지, 면접답변인지, 일반 텍스트인지 구분합니다."""
    classify_prompt = PromptTemplate.from_template(
        """
        다음 입력이 어떤 유형인지 판단하세요: 
        - 자소서 (resume)
        - 면접 질문에 대한 답변 (interview_answer)
        - 그 외 일반 텍스트 (other)

        입력:
        {input}

        형식: resume, interview_answer, other 중 하나로만 답하세요.
        """
    )
    chain = classify_prompt | llm | JsonOutputParser()
    return chain.invoke({"input": input})


@tool
def generate_reasoning(data):
    """Resumes, Job Descriptions, and Company Info를 기반으로 질문 이유(Reasoning)를 도출"""

    data = json.loads(data)
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
    chain = reasoning_prompt | llm | JsonOutputParser()
    return chain.invoke({"resume": resume, "jd": jd, "company": company})


@tool
def generate_acting(reasoning):
    """Reasoning에 기반하여 실제 면접 질문을 생성"""
    acting_prompt = PromptTemplate.from_template(
        """
        다음은 면접 질문을 만들기 위한 Reasoning입니다:

        {reasoning}

        이 정보를 바탕으로, 적절한 면접 질문 1개를 출력하세요.
        [예시 출력]
        - 협업 경험 중 가장 도전적이었던 상황은 무엇이었나요?
        """
    )
    chain = acting_prompt | llm | JsonOutputParser()
    return chain.invoke({"reasoning": reasoning})


@tool
def translate_to_korean(text: str) -> str:
    """영어 텍스트를 자연스러운 한국어로 번역합니다."""
    translate_prompt = PromptTemplate.from_template(
        """
    다음 영어 문장을 자연스러운 한국어로 번역하세요.

    영어:
    {text}

    한국어:
    """
    )
    chain = translate_prompt | llm | JsonOutputParser()
    return chain.invoke({"text": text})


tools = [classify_input, generate_reasoning, generate_acting, translate_to_korean]


def parse_role_from_message(
    message: BaseMessage,
) -> Literal["assistant", "human", "system", "tool", "unknown"]:
    """Extract role from a message"""
    if isinstance(message, AIMessage):
        return "assistant"
    elif isinstance(message, HumanMessage):
        return "human"
    elif isinstance(message, SystemMessage):
        return "system"
    elif isinstance(message, ToolMessage):
        return "tool"
    else:
        return "unknown"


# agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
prompt = PromptTemplate.from_template(
    """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""
)

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def run_interview_question_pipeline(resume: str, jd: str, company: str) -> str:
    return agent_executor.invoke(
        f"generate_interview_question(resume='{resume}', jd='{jd}', company='{company}')"
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

            후속 질문은 이전 질문/답변 쌍들을 보면서 면접관이 지원자에게 검증하고자 하는 핵심적인 포인트를 파악하기위한 목적이다.
            후속 질문은 반드시 지원자의 답변에 대한 후속질문이어야 한다.

            """,
    )

    return followup_prompt | llm | StrOutputParser()


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
    return evaluate_prompt | llm | StrOutputParser()


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

    return model_answer_prompt | llm | StrOutputParser()


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
