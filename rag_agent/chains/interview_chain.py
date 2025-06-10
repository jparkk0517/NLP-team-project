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
from langchain import hub
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


# LLM 초기화
logger.info("Starting interview chain initialization...")
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model_name="gpt-4o-mini"
)

@tool
def classify_input(input_data: str) -> str:
    """사용자 입력과, 이전 대화내용을 바탕으로 현재 입력이 어떤 형식인지 분류합니다."""
    try:
        data = json.loads(input_data)
        request = data.get("request", "")
        chat_history = data.get("chat_history", "")
    except json.JSONDecodeError:
        # JSON이 아닌 경우 직접 처리
        request = input_data
        chat_history = ""

    classify_prompt = PromptTemplate.from_template(
        """
        다음 입력이 어떤 유형인지 판단하세요: 
        - 자소서 입력 (resume)
        - 질문 요청 (question)
        - 꼬리질문 요청 (followup)
        - 모범 답변 요청 (modelAnswer)
        - 답변 요청 (answer)
        - 그 외 일반 텍스트 (other)

        입력:
        사용자 입력: {request}
        이전 대화 내용: {chat_history}

        형식: resume, question, followup, modelAnswer, answer, other 중 하나로만 답하세요.
        """
    )
    chain = classify_prompt | llm | StrOutputParser()
    return chain.invoke({"request": request, "chat_history": chat_history})

@tool
def generate_question_reasoning(data: str) -> str:
    """자소서, JD, 회사 정보를 기반으로 질문 이유(Reasoning)를 도출합니다."""
    try:
        parsed_data = json.loads(data)
        resume = parsed_data.get("resume", "")
        jd = parsed_data.get("jd", "")
        company = parsed_data.get("company", "")
        persona = parsed_data.get("persona", "")
    except json.JSONDecodeError:
        return "입력 데이터 형식이 올바르지 않습니다. JSON 형식으로 제공해주세요."

    reasoning_prompt = PromptTemplate.from_template(
        """
        다음은 지원자의 자소서, JD(직무기술서), 회사 정보, 그리고 면접관 페르소나입니다:

        자기소개서:
        {resume}

        JD:
        {jd}

        회사 정보:
        {company}

        면접관 페르소나:
        {persona}

        당신은 위 페르소나를 기반으로 하는 면접관입니다.
        다음을 고려하여 질문 생성의 이유(Reasoning)를 작성하세요:

        1. 회사 인재상에 부합하는 성격/역량/행동을 자소서에서 얼마나 확인할 수 있는가?
        2. JD에서 요구하는 자격요건, 기술, 경험과 자소서가 얼마나 부합하는가?
        3. 부족하거나 확인이 필요한 부분은 무엇인가?
        4. 면접관 페르소나의 시각과 말투, 성격을 반영한 분석

        Reasoning을 명확하고 논리적으로 작성하세요.
        
        출력 예시:
        - (논리적 스타일) "JD에서 요구한 협업 경험이 자소서에 구체적으로 드러나지 않아, 실제로 팀 프로젝트를 주도한 경험이 있었는지 확인하고 싶다."
        - (호기심 많은 스타일) "지원자는 데이터 분석 경험이 있다고 했지만 어떤 툴을 사용했는지 궁금하다. 프로젝트 맥락을 더 듣고 싶다."
        """
    )

    chain = reasoning_prompt | llm | StrOutputParser()
    return chain.invoke({
        "resume": resume, 
        "jd": jd, 
        "company": company, 
        "persona": persona
    })

@tool
def generate_question_acting(reasoning: str) -> str:
    """Reasoning에 기반하여 실제 면접 질문을 생성합니다."""
    acting_prompt = PromptTemplate.from_template(
        """
        다음은 면접 질문을 만들기 위한 Reasoning입니다:

        {reasoning}

        이 정보를 바탕으로 적절한 면접 질문 1개를 생성하세요.
        질문은 구체적이고 답변 가능하도록 작성하세요.
        
        질문:
        """
    )

    chain = acting_prompt | llm | StrOutputParser()
    return chain.invoke({"reasoning": reasoning})

@tool
def generate_followup_reasoning(input_data: str) -> str:
    """지원자의 답변에 대한 꼬리질문 생성을 위한 Reasoning을 도출합니다."""
    try:
        data = json.loads(input_data)
        chat_history = data.get("chat_history", "")
        input_text = data.get("input_text", "")
    except json.JSONDecodeError:
        input_text = input_data
        chat_history = ""

    reasoning_prompt = PromptTemplate.from_template(
        """
        아래는 AI 면접 시스템에서 지금까지 진행된 대화입니다:

        대화 이력:
        {chat_history}

        현재 질문에 대한 지원자의 답변:
        "{input_text}"

        이 답변을 바탕으로 꼬리질문을 생성하기 위한 면접관의 Reasoning을 작성하세요.
        지원자의 답변에서 구체적이지 않은 부분, 추가 설명이 필요한 포인트를 찾아내세요.
        """
    )

    chain = reasoning_prompt | llm | StrOutputParser()
    return chain.invoke({
        "chat_history": chat_history,
        "input_text": input_text
    })

@tool
def generate_followup_acting(input_data: str) -> str:
    """Reasoning과 지원자 답변을 기반으로 꼬리질문을 생성합니다."""
    try:
        data = json.loads(input_data)
        reasoning = data.get("reasoning", "")
        input_text = data.get("input_text", "")
    except json.JSONDecodeError:
        return "입력 데이터 형식이 올바르지 않습니다."

    prompt = PromptTemplate.from_template(
        """
        [지원자 답변]
        {input_text}

        [면접관의 Reasoning]
        {reasoning}

        위 Reasoning을 바탕으로 자연스럽고 구체적인 꼬리질문을 한 문장으로 작성하세요.
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
def evaluate_answer(data: str) -> dict:
    """지원자 답변을 종합적으로 평가합니다."""
    parser = JsonOutputParser(pydantic_object=AssessmentResult)
    
    try:
        parsed_data = json.loads(data)
        resume = parsed_data.get("resume", "")
        jd = parsed_data.get("jd", "")
        company = parsed_data.get("company", "")
        question = parsed_data.get("question", "")
        answer = parsed_data.get("answer", "")
        persona = parsed_data.get("persona", "")
    except json.JSONDecodeError:
        return {"error": "입력 데이터 형식이 올바르지 않습니다."}

    assessment_prompt = PromptTemplate(
        input_variables=["resume", "jd", "company", "question", "answer", "persona"],
        template="""
        역할: 면접관으로서 지원자의 답변을 평가합니다.

        직무 설명:
        {jd}

        이력서:
        {resume}

        회사 정보:
        {company}

        질문: 
        {question}
        
        지원자의 답변:
        {answer}

        면접관 정보:
        {persona}
        
        다음 4개 항목을 0-10점으로 평가하세요:
        1. 논리성 (logicScore): 답변의 논리적 일관성과 구조
        2. 직무적합성 (jobFitScore): JD 요구사항과의 부합도
        3. 핵심가치 부합성 (coreValueFitScore): 회사 가치와의 일치도
        4. 커뮤니케이션 능력 (communicationScore): 의사소통 명확성

        {format_instructions}
        """,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = assessment_prompt | llm | parser
    
    try:
        result = chain.invoke({
            "jd": jd,
            "resume": resume,
            "company": company,
            "question": question,
            "answer": answer,
            "persona": persona,
        })
        return result
    except Exception as e:
        logger.error(f"평가 중 오류 발생: {e}")
        return {"error": "평가 중 오류가 발생했습니다."}

tools = [
    classify_input,
    generate_question_reasoning,
    generate_question_acting,
]


def parse_role_from_message(message: BaseMessage) -> Literal["assistant", "human", "system", "tool", "unknown"]:
    """메시지에서 역할을 추출합니다."""
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


# ReAct 프롬프트 (langchain hub에서 가져오기)
try:
    # LangChain Hub에서 표준 ReAct 프롬프트 가져오기
    prompt = hub.pull("hwchase17/react")
except:
    # Hub를 사용할 수 없는 경우 커스텀 프롬프트 사용
    prompt = PromptTemplate.from_template(
        """
        당신은 전문 면접관입니다. 다음 도구들을 사용하여 효과적인 면접을 진행하세요:

        {tools}

        다음 형식을 사용하세요:

        Question: 답변해야 할 입력 질문
        Thought: 무엇을 해야 할지 생각하세요
        Action: 수행할 작업, 다음 중 하나여야 합니다: [{tool_names}]
        Action Input: 작업에 대한 입력
        Observation: 작업의 결과
        ... (이 Thought/Action/Action Input/Observation은 N번 반복될 수 있습니다)
        Thought: 이제 최종 답변을 알았습니다
        Final Answer: 원래 입력 질문에 대한 최종 답변

        시작!

        Question: {input}
        Thought: {agent_scratchpad}
        """
    )

# memory = MemorySaver()
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True,
    max_iterations=3,  # 최대 반복 횟수 제한
    handle_parsing_errors=True  # 파싱 오류 처리
)

class InterviewAgent:
    """면접관 Agent 클래스"""
    
    def __init__(self):
        self.agent_executor = agent_executor
        self.logger = logger
    
    def run_interview(self, input_data: dict) -> str:
        """면접 진행"""
        try:
            # 입력 데이터를 JSON 문자열로 변환
            input_json = json.dumps(input_data, ensure_ascii=False)
            
            # Agent 실행
            result = self.agent_executor.invoke({
                "input": input_json
            })
            
            return result.get("output", "응답을 생성할 수 없습니다.")
            
        except Exception as e:
            self.logger.error(f"면접 진행 중 오류 발생: {e}")
            return f"오류가 발생했습니다: {str(e)}"
    
    def generate_question(self, resume: str, jd: str, company: str, persona: str = "") -> str:
        """질문 생성"""
        input_data = {
            "action": "generate_question",
            "resume": resume,
            "jd": jd,
            "company": company,
            "persona": persona
        }
        return self.run_interview(input_data)
    
    def generate_followup(self, chat_history: str, current_answer: str) -> str:
        """꼬리질문 생성"""
        input_data = {
            "action": "generate_followup",
            "chat_history": chat_history,
            "current_answer": current_answer
        }
        return self.run_interview(input_data)
    
    def evaluate_response(self, resume: str, jd: str, company: str, 
                         question: str, answer: str, persona: str = "") -> dict:
        """답변 평가"""
        input_data = {
            "action": "evaluate",
            "resume": resume,
            "jd": jd,
            "company": company,
            "question": question,
            "answer": answer,
            "persona": persona
        }
        result = self.run_interview(input_data)
        try:
            return json.loads(result)
        except:
            return {"error": "평가 결과를 파싱할 수 없습니다."}


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
