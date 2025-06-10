from pydantic import BaseModel
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from typing import Literal
import os
import logging
import json


from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    chain = classify_prompt | llm | StrOutputParser()
    return chain.invoke({"input": input})


@tool
def generate_question_reasoning(data):
    """Resumes, Job Descriptions, and Company Info를 기반으로 질문 이유(Reasoning)를 도출"""

    data = json.loads(data)
    resume = data.get("resume", "")
    jd = data.get("jd", "")
    company = data.get("company", "")
    # chat_history = data["chat_history"]
    persona = data.get("persona", "")

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
    return chain.invoke(
        {"resume": resume, "jd": jd, "company": company, "persona": persona}
    )


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


@tool
def generate_followup_reasoning(input_text):
    """지원자의 답변에 대한 꼬리질문 생성을 위해 지원자 답변 및 이전 대화내용을 기반으로 꼬리질문 이유(Reasoning) 도출"""

    reasoning_prompt = PromptTemplate.from_template(
        """
        아래는 AI 면접 시스템에서 지금까지 진행된 질문과 지원자의 답변입니다:

        대화 이력:
        {chat_history}

        현재 질문에 대한 지원자의 답변은 다음과 같습니다:
        "{input_text}"

        이 답변을 바탕으로 다음 꼬리질문을 이어가려는 면접관의 Reasoning을 작성하세요.
        예를 들어, 지원자의 말 중 구체적이지 않은 부분을 짚거나, 경험의 진정성, 추가 설명이 필요한 포인트를 찾아내세요.
        """
    )

    chain = reasoning_prompt | llm | StrOutputParser()
    return chain.invoke({})


@tool
def generate_followup_acting(reasoning, input_text):
    """Reasoning과 사용자의 답변을 기반으로 꼬리질문 생성"""

    prompt = PromptTemplate.from_template(
        """
        아래는 지원자의 답변과 그에 대한 면접관의 추론(Reasoning)입니다.

        [지원자 답변]
        {input_text}

        [면접관의 Reasoning]
        {reasoning}

        위 Reasoning을 바탕으로 다음 꼬리질문을 작성하세요.
        질문은 면접에서 실제로 사용할 수 있도록 자연스럽고 구체적으로 표현하세요.
        한 문장으로 작성하세요.
        """
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"reasoning": reasoning, "input_text": input_text})


class AssessmentResult(BaseModel):
    logicScore: int
    jobFitScore: int
    coreValueFitScore: int
    communicationScore: int
    averageScore: float
@tool
def evaluate_answer(data):
    """지원자 답변을 평가"""


    parser = JsonOutputParser(pydantic_object=AssessmentResult)

    data = json.loads(data)
    resume = data.get("resume", "")
    jd = data.get("jd", "")
    company = data.get("company", "")
    question = data.get("question", "")
    answer = data.get("answer", "")
    persona = data.get("persona", "")

    assessment_prompt = PromptTemplate(
        input_variables=["resume", "jd", "company", "chat_history"],
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
            {company}

            이전 질문: 
            {question}
            
            지원자의 답변:
            {answer}

            면접관 정보:
            {persona}
            
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

    chain = assessment_prompt | llm | parser

    return chain.invoke(
        {
            "jd": jd,
            "resume": resume,
            "company": company,
            "question": question,
            "answer": answer,
            "persona": persona,
        }
    )


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
    chain = translate_prompt | llm | StrOutputParser()
    return chain.invoke({"text": text})


tools = [
    classify_input,
    generate_question_reasoning,
    generate_question_acting,
    translate_to_korean,
]


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
Thought: {agent_scratchpad}
"""
)

# LLM 초기화
logger.info("Starting interview chain initialization...")
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model_name="gpt-4o-mini"
)

# memory = MemorySaver()
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
            답변은 다음 형식을 따라야 합니다:

            1. STAR 기법을 활용한 구조화된 답변:
               - Situation: 상황 설명
               - Task: 해결해야 할 과제
               - Action: 취한 행동
               - Result: 결과와 배운 점

            2. 직무 관련성:
               - JD에서 요구하는 역량과의 연관성
               - 회사의 핵심 가치와의 부합성

            3. 구체성:
               - 구체적인 숫자와 데이터 포함
               - 실제 경험 기반의 예시

            4. 논리성:
               - 명확한 인과관계
               - 체계적인 설명

            답변은 한글로 생성해야 한다.
        """,
    )

    model_answer_chain = LLMChain(
        llm=llm, prompt=model_answer_prompt, output_key="result"
    )
    return model_answer_chain


def get_initial_message_chain():
    initial_prompt = PromptTemplate(
        template="""
        당신은 AI 면접 시뮬레이터입니다. 사용자가 면접을 시작할 수 있도록 안내하는 첫 메시지를 작성하세요.

        조건:
        - 사용자가 당신이 AI 면접관임을 이해할 수 있어야 합니다.
        - 사용자가 자소서(이력서)를 먼저 입력해야 한다는 점을 꼭 설명하세요.
        - 너무 딱딱하거나 기계적이지 않고, 친절하고 격려하는 말투로 작성하세요.
        - 한 문단(2~4줄) 분량의 짧은 인삿말로 작성하고, 짧은 호흡으로 줄바꿈(\n)하세요.

        예시1:
        안녕하세요! 저는 여러분의 면접을 도와드릴 AI 시뮬레이터입니다. 👋
        저는 자소서를 기반으로 예상 면접 질문을 생성하고, 
        사용자의 답변을 분석하여 피드백을 제공하는 서비스를 제공합니다.
        면접을 시작하려면 먼저 본인의 이력서(자기소개서)를 입력해 주세요.
        입력하신 내용을 바탕으로 면접 질문을 생성하고 면접을 시작해보겠습니다.

        예시2:
        AI 면접 시뮬레이터에 오신 것을 환영합니다 :) 
        먼저 자소서(이력서)를 입력해 주세요.
        해당 내용을 분석해 면접 질문을 생성하고 면접을 시작해보겠습니다.

        예시3:
        반갑습니다! 지금부터 AI가 면접관 역할을 대신해드릴게요. 
        시작하려면 본인의 이력서(자기소개서)를 입력해 주세요.
        입력하신 내용을 바탕으로 면접 질문을 생성하고 면접을 시작해보겠습니다. 🔥
        """
    )
    initial_chain = LLMChain(llm=llm, prompt=initial_prompt, output_key="result")
    return initial_chain


def get_reranking_model_answer_chain():
    reranking_prompt = PromptTemplate(
        input_variables=[
            "resume",
            "jd",
            "company_infos",
            "question",
            "prev_question_answer_pairs",
        ],
        template="""
            역할:
            당신은 면접관입니다. 주어진 질문에 대해 최적의 답변을 생성해야 합니다.
            이 답변은 회사의 가치관, 직무 요구사항, 그리고 이력서의 내용을 모두 고려해야 합니다.

            상황:
            {company_infos}

            이력서:
            {resume}

            직무 설명:
            {jd}

            이전 질문/답변 쌍들:
            {prev_question_answer_pairs}

            현재 질문:
            {question}

            다음 단계로 답변을 생성하세요:
            1. 회사의 가치관과 직무 요구사항을 분석
            2. 이력서에서 관련된 경험과 역량을 찾아 연결
            3. 이전 대화 맥락을 고려하여 일관성 있는 답변 구성
            4. 구체적이고 명확한 예시를 포함
            5. 회사의 가치관과 부합하는 방식으로 답변 마무리

            답변은 한글로 생성해야 한다.
            """,
    )

    reranking_chain = LLMChain(llm=llm, prompt=reranking_prompt, output_key="result")
    return reranking_chain


def compare_model_answers(original_answer: str, reranked_answer: str) -> dict:
    """두 모델 답변을 비교하는 함수"""
    comparison_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
당신은 두 개의 면접 답변을 평가하는 인사 전문가입니다.
다음 기준에 따라 두 답변을 비교하세요:
1. 구체성: 예시와 경험이 얼마나 구체적으로 제시되었는가?
2. 관련성: 답변이 질문과 직무 요구사항에 얼마나 부합하는가?
3. 구조화: 답변이 얼마나 논리적이고 명확하게 구성되어 있는가?
4. 회사 적합성: 답변이 회사의 가치관과 문화에 얼마나 부합하는가?
5. 전문성: 답변이 직무 관련 지식과 역량을 얼마나 잘 보여주는가?

각 기준별로
- 원본 답변과 reranking 답변 각각 1~10점으로 평가
- 간단한 설명
- 어떤 답변이 더 나은지

아래와 같은 JSON 형식으로만 결과를 반환하세요(추가 설명, 코드블록 등 금지):
{{
    "specificity": {{
        "original_score": number,
        "reranked_score": number,
        "explanation": string,
        "better_answer": "original" 또는 "reranked"
    }},
    "relevance": {{
        "original_score": number,
        "reranked_score": number,
        "explanation": string,
        "better_answer": "original" 또는 "reranked"
    }},
    "structure": {{
        "original_score": number,
        "reranked_score": number,
        "explanation": string,
        "better_answer": "original" 또는 "reranked"
    }},
    "company_fit": {{
        "original_score": number,
        "reranked_score": number,
        "explanation": string,
        "better_answer": "original" 또는 "reranked"
    }},
    "expertise": {{
        "original_score": number,
        "reranked_score": number,
        "explanation": string,
        "better_answer": "original" 또는 "reranked"
    }},
    "overall": {{
        "original_total": number,
        "reranked_total": number,
        "better_answer": "original" 또는 "reranked",
        "summary": string
    }}
}}
모든 설명과 결과는 반드시 한국어로 작성하세요.
""",
            ),
            (
                "user",
                """다음 두 답변을 비교하세요:

원본 답변:
{original_answer}

Reranking 답변:
{reranked_answer}""",
            ),
        ]
    )

    chain = comparison_prompt | llm | StrOutputParser()

    try:
        result = chain.invoke(
            {"original_answer": original_answer, "reranked_answer": reranked_answer}
        )
        # 코드블록 등 제거
        import re

        result_str = result.strip()
        # ```json ... ``` 또는 ``` ... ``` 제거
        result_str = re.sub(
            r"^```(?:json)?|```$", "", result_str, flags=re.MULTILINE
        ).strip()
        comparison_result = json.loads(result_str)
        return comparison_result
    except Exception as e:
        logger.error(f"Error in comparing answers: {str(e)}")
        raise Exception(f"Failed to compare answers: {str(e)}")
