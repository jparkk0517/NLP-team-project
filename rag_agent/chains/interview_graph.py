from dotenv import load_dotenv
from ..persona.PersonaService import PersonaService

from pydantic import BaseModel, Field

import os
from typing import Literal

from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import START, END

from typing import TypedDict

from rag_agent import ChatHistory

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent

import os

load_dotenv()

from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from rag_agent import ChatHistory


class Route(BaseModel):
    target: Literal['question', 'model_answer', 'followup', 'llm'] = Field(
        description="The target for the query to answer"
    )


class AgentState(TypedDict):
    query: str  # 사용자 답변
    answer: str  # Agent 답변
    input_type: str  # 사용자 답변 유형
    persona_id: str  # 페르소나 ID
    route_type: str  # routing 결과
    resume: str  # 자소서(이력서)
    jd: str  # 채용공고
    company: str  # 회사정보 (인재상)
    chat_history: ChatHistory  # 대화내역
    last_question: str  # 마지막 질문


llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model_name="gpt-4o-mini"
)

def classify_input(state: AgentState) -> AgentState:
    """
    사용자 입력과, 이전 대화내용을 바탕으로 현재 입력이 어떤 형식인지 분류하고,
    결과를 router node로 전달합니다.

    Args:
      state (AgentState): 현재 메시지 상태를 나타내는 객체입니다.

    Returns:
      Command: router node로 이동하기 위한 명령을 반환합니다.
    """

    query = state.get("query", "")
    print("classify_input > query >", query)
    
    classify_prompt = PromptTemplate.from_template("""
주어진 query와 chat_history를 바탕으로 입력이 어떤 유형인지 판단하세요: 
- 면접질문 요청 (question)
- 꼬리질문 요청 (followup)
- 모범답변 요청 (modelAnswer)
- 답변 (answer)
- 그 외 면접과 관련 없는 텍스트 (other)


사용자 입력:
{query}

형식: question, followup, modelAnswer, answer, other 중 하나로만 답하세요.""")
    
    router_chain = classify_prompt | llm | StrOutputParser() 
    result = router_chain.invoke({'query': query})
    
    print("classify_input > result >", result)
    
    # 결과 메시지를 업데이트하고 router node로 이동합니다.
    return { 
        "input_type": result
    }


persona_service = PersonaService.get_instance()
chat_history = ChatHistory.get_instance()


def assign_persona_node(state: AgentState) -> AgentState:
    """페르소나 할당 node입니다. 주어진 state를 기반으로 assign_persona 에이전트를 호출하고,
결과를 router node로 전달합니다.

Args:
    state (AgentState): 현재 메시지 상태 객체.

Returns:
    Command: router node로 이동 명령을 반환."""
    
    resume = state.get("resume", "")
    jd = state.get("jd", "")
    company = state.get("company", "")
    query = state.get("query", "")
    last_question = state.get("last_question", "")
    persona_id = persona_service.invoke_agent(resume, jd, company, query, last_question)
    print("assign_persona_node > persona_id >", persona_id)

    return {"persona_id": persona_id}


def router(state: AgentState) -> AgentState:
    """
    주어진 state에서 input_type를 기반으로 적절한 경로를 결정합니다.

    Args:
        state (AgentState): 현재 에이전트의 state를 나타내는 객체입니다.

    Returns:
        Literal['question', 'model_answer', 'followup', 'llm']: 쿼리에 따라 선택된 경로를 반환합니다.
    """
    
    query = state["query"]
    router_system_prompt = """
You are an expert at routing a user's input type to 'question', 'model_answer', 'followup' or 'llm'.
If the user input is 'question' route to 'question'.
else if the user input is 'model_answer' route to 'model_answer',
else if the user input is 'followup' route to 'followup',

if you think the input is not related to either 'question', 'model_answer' or 'followup';
you can route it to 'llm'."""

    router_prompt = ChatPromptTemplate.from_messages(
        [("system", router_system_prompt), ("user", "{query}")]
    )

    structured_router_llm = llm.with_structured_output(Route)

    router_chain = router_prompt | structured_router_llm
    route = router_chain.invoke({"query": query})
    print("router", route)

    return { "route_type": route }


def generation(state: AgentState) -> AgentState:
    """
    사용자 입력과, 이전 대화내용을 바탕으로 면접 질문을 생성하고,
    결과를 router node로 전달합니다.

    Args:
      state (MessageState): 현재 메시지 상태를 나타내는 객체입니다.

    Returns:
      Command: router node로 이동하기 위한 명령을 반환합니다.
    """
    try:
        # 상태에서 필요한 정보 추출
        resume = state.get("resume", "")
        jd = state.get("jd", "")
        company = state.get("company", "")
        persona = state.get("persona", "")

        generation_prompt = PromptTemplate.from_template(
            """다음은 지원자의 자소서, JD(직무기술서), 회사 정보, 그리고 면접관 페르소나입니다:

            자기소개서:
            {resume}

            JD:
            {jd}

            회사 정보:
            {company}

            면접관 페르소나:
            {persona}

            당신은 위 페르소나를 기반으로 하는 면접관입니다.
            다음 단계를 거쳐 면접 질문을 생성하세요:

            1단계 - 분석 (Reasoning):
            - 회사 인재상에 부합하는 성격/역량/행동을 자소서에서 얼마나 확인할 수 있는가?
            - JD에서 요구하는 자격요건, 기술, 경험과 자소서가 얼마나 부합하는가?
            - 부족하거나 확인이 필요한 부분은 무엇인가?
            - 면접관 페르소나의 시각과 말투, 성격을 반영한 분석

            2단계 - 질문 생성 (Acting):
            - 1단계 분석을 바탕으로 구체적이고 답변 가능한 면접 질문 1개를 생성
            - 면접관 페르소나의 말투와 스타일을 반영

            출력 형식:
            [생성된 면접 질문]
            """
        )

        chain = generation_prompt | llm | StrOutputParser()
        result = chain.invoke(
            {"resume": resume, "jd": jd, "company": company, "persona": persona}
        )
        print("result", result)

        # 결과를 상태에 업데이트
        return {"answer": result}

    except Exception as e:
        return {
            "error": f"Generation 노드에서 오류 발생: {str(e)}",
            "status": "error",
            "messages": state.get("messages", [])
            + [{"role": "system", "content": f"오류: {str(e)}"}],
        }


def followup(state: AgentState) -> AgentState:
    """
    사용자 입력과, 이전 대화내용을 바탕으로 현재 입력에 대한 꼬리질문을 생성하고,
    결과를 router node로 전달합니다.

    Args:
      state (MessageState): 현재 메시지 상태를 나타내는 객체입니다.

    Returns:
      Command: router node로 이동하기 위한 명령을 반환합니다.
    """
    try:
        # 상태에서 필요한 정보 추출
        resume = state.get("resume", "")
        jd = state.get("jd", "")
        company = state.get("company", "")
        persona = state.get("persona", "")
        chat_history = state.get("chat_history", "")
        query = state.get("query", "")

        followup_prompt = PromptTemplate.from_template(
            """아래는 AI 면접 시스템에서 지금까지 진행된 대화입니다:

대화 이력:
{chat_history}

현재 질문에 대한 지원자의 답변:
{query}

자기소개서:
{resume}

JD:
{jd}

회사 정보:
{company}

면접관 페르소나:
{persona}

당신은 위 페르소나를 기반으로 하는 면접관입니다.
다음 단계를 거쳐 면접 질문을 생성하세요:

1단계 - 분석 (Reasoning):
- 회사 인재상에 부합하는 성격/역량/행동을 자소서에서 얼마나 확인할 수 있는가?
- JD에서 요구하는 자격요건, 기술, 경험과 자소서가 얼마나 부합하는가?
- 부족하거나 확인이 필요한 부분은 무엇인가?
- 면접관 페르소나의 시각과 말투, 성격을 반영한 분석

2단계 - 질문 생성 (Follow-up Question):
- 1단계 분석을 바탕으로 구체적이고 답변 가능한 면접 질문 1개를 생성
- 면접관 페르소나의 말투와 스타일을 반영

출력 형식:
[생성된 꼬리 면접 질문]
"""
        )

        chain = followup_prompt | llm | StrOutputParser()
        result = chain.invoke(
            {
                "resume": resume,
                "jd": jd,
                "company": company,
                "persona": persona,
                "chat_history": chat_history,
                "query": query,
            }
        )
        print("result", result)

        # 결과를 상태에 업데이트
        return {"answer": result}

    except Exception as e:
        return {
            "error": f"Followup 노드에서 오류 발생: {str(e)}",
            "status": "error",
            "messages": state.get("messages", [])
            + [{"role": "system", "content": f"오류: {str(e)}"}],
        }


def call_llm(state: AgentState) -> AgentState:
    """
    주어진 state에서 쿼리를 LLM에 전달하여 응답을 얻습니다.

    Args:
        state (AgentState): 현재 에이전트의 state를 나타내는 객체입니다.

    Returns:
        AgentState: 'answer' 키를 포함하는 새로운 state를 반환합니다.
    """
    query = state['query']
    llm_chain = llm | StrOutputParser()
    llm_answer = llm_chain.invoke(query)
    return {'answer': llm_answer }


def conditional_router(state: AgentState) -> str:
    """
    그래프의 조건부 엣지에서 사용할 라우팅 함수

    Args:
        state (AgentState): 현재 상태

    Returns:
        str: 다음 노드 이름
    """
    # 상태에서 라우팅 정보 확인
    print(state)
    next_route = state.get("next_route", "other")

    # 그래프 노드 이름과 매핑
    route_mapping = {
        'generation': 'generation',
        'question': 'generation',
        'answer': 'generation',
        'followup': 'followup',
        'model_answer': 'ModelAnswer', 
        'interview_answer': 'EvaluateFollowup',
        'other': 'llm'
    }
    
    return route_mapping.get(next_route, 'llm')


class GraphAgent:
    def __init__(
        self,
        resume: str,
        jd: str,
        company: str,
    ):
        self.resume = resume
        self.jd = jd
        self.company = company
        graph_builder = StateGraph(AgentState)

        # 노드 추가
        graph_builder.add_node("classify_input", classify_input)
        graph_builder.add_node("assign_persona", assign_persona_node)
        graph_builder.add_node("router", router)
        graph_builder.add_node("generation", generation)
        graph_builder.add_node("followup", followup)
        graph_builder.add_node('llm', call_llm)

        # 시작점에서 병렬 실행
        graph_builder.add_edge(START, "classify_input")
        graph_builder.add_edge(START, "assign_persona")

        # 두 병렬 노드가 완료되면 라우터로
        graph_builder.add_edge("classify_input", "router")
        graph_builder.add_edge("assign_persona", "router")

        # 생성 노드에서 종료
        graph_builder.add_edge("generation", END)
        graph_builder.add_edge('followup', END)
        graph_builder.add_edge('llm', END)

        graph_builder.add_conditional_edges(
            "router",
            conditional_router,
            {"generation": "generation", "followup": "followup", "llm": "llm"},
        )

        self.graph = graph_builder.compile()

    def run(self, query: str) -> str:
        initial_state = {
            "query": query,
            "resume": self.resume,
            "jd": self.jd,
            "company": self.company,
            "chat_history": chat_history.get_all_history_as_string(),
            "last_question": chat_history.get_question_by_id(
                chat_history.get_latest_question_id()
            ),
        }
        return self.graph.invoke(initial_state)
