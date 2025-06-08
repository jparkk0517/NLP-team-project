from typing import List, Optional, Self

from rag_agent.chat_history.ChatHistory import ChatHistory

# rag_agent.chat_history.ChatHistory는 이 예제에서 직접 사용되지 않지만, 필요시 통합 가능
# from rag_agent.chat_history.ChatHistory import ChatHistory
from .Persona import Persona, PersonaType, llm  # Persona 클래스와 LLM 임포트
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import os
from langchain.agents import AgentExecutor, create_react_agent

# tools.py 같은 별도 파일로 분리했다면 from .tools import assign_interviewer_persona, generate_interview_question, generate_model_answer_and_evaluation
from __main__ import (
    assign_interviewer_persona,
    generate_interview_question,
    generate_model_answer_and_evaluation,
)
import json  # JSON 직렬화를 위해 필요

# .env 파일 로드 (이미 위에서 로드됨)
load_dotenv()

# --- Agent의 기본 프롬프트 (ReAct 패턴) ---
# 이 프롬프트는 AgentExecutor가 Agent에게 어떤 도구를 사용할지, 어떻게 생각하고 행동할지를 지시합니다.
AGENT_BASE_PROMPT = PromptTemplate.from_template(
    """
    당신은 면접 과정을 돕는 유능한 AI 어시스턴트입니다.
    사용자의 요청에 따라 적절한 면접관 페르소나를 할당하거나,
    할당된 페르소나의 관점에서 면접 질문을 생성하거나,
    지원자의 답변을 평가하고 모범 답변을 생성하는 도구들을 활용합니다.
    
    질문, 이력서, 직무 설명, 회사 자료, 지원자 답변 등 주어진 모든 정보를 최대한 활용하세요.
    최종 결과는 항상 사용자에게 명확하고 유용한 형태로 제공해야 합니다.
    
    You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer (이것은 사용자 쿼리입니다)
    Thought: you should always think about what to do next, considering the user's intent and available tools.
             Do I need to assign a persona? Do I need to generate a question? Do I need to evaluate an answer?
             What information do I need for the tool?
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action (This should be a JSON string if the tool expects JSON)
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer or I have completed the task.
    Final Answer: the final answer or task completion message to the original input question.

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}
    """
)

chat_history = ChatHistory.get_instance()


class PersonaService:
    _instance: Self | None = None

    @classmethod
    def get_instance(cls) -> Self:
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # 중복 초기화 방지
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.persona_list: List[Persona] = []

        # --- Agent 구축 ---
        # 1. Agent가 사용할 도구들을 정의합니다.
        # 이 도구들은 위에서 정의한 `@tool` 함수들입니다.
        self.tools = [
            assign_interviewer_persona,
            generate_interview_question,
            generate_model_answer_and_evaluation,
            # 필요시 다른 도구 추가
        ]

        # 2. ReAct Agent를 생성합니다.
        # create_react_agent는 LLM, 도구들, 프롬프트 템플릿을 받아 Agent 체인을 생성합니다.
        self.agent = create_react_agent(llm, self.tools, AGENT_BASE_PROMPT)

        # 3. AgentExecutor를 생성합니다.
        # AgentExecutor는 Agent를 실행하고, 도구 실행 루프를 관리합니다.
        # verbose=True로 설정하면 Agent의 Thought/Action/Observation 과정을 콘솔에 출력합니다.
        # handle_parsing_errors=True는 LLM이 유효하지 않은 Action/Action Input을 생성했을 때 처리합니다.
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,  # 파싱 에러 발생 시 처리
            # memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True) # 다중 턴 대화 시
        )

        self._initialized = True

    def __new__(cls, *args, **kwargs) -> Self:
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_persona(self, persona: Persona):
        self.persona_list.append(persona)

    def get_persona_list(self) -> List[Persona]:
        return self.persona_list

    def delete_persona(self, persona_id: str):
        self.persona_list = [p for p in self.persona_list if p.id != persona_id]

    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        for persona in self.persona_list:
            if persona.id == persona_id:
                return persona
        return None

    async def invoke_agent(
        self,
        user_query: str,
        resume_summary: str,
        jd_summary: str,
        company_infos_summary: Optional[str] = None,
        applicant_answer: Optional[str] = None,
        interviewer_question: Optional[str] = None,  # 지원자가 받은 질문
    ) -> str:
        """
        Agent를 호출하여 사용자 쿼리에 대한 응답을 생성합니다.
        다양한 면접 관련 맥락 정보를 Agent에 전달합니다.
        """
        # 현재 등록된 페르소나 리스트를 JSON 문자열로 변환하여 도구에 전달할 준비
        available_personas_for_tool = json.dumps(
            [p.to_dict() for p in self.persona_list], ensure_ascii=False
        )

        # Agent의 'input'에 전달할 맥락 정보 딕셔너리 구성
        # 이 정보들은 Agent의 Thought 과정에서 도구 인자로 활용될 수 있도록 LLM이 참조합니다.
        context_for_agent_input = {
            "user_query": user_query,
            "resume_summary": resume_summary,
            "jd_summary": jd_summary,
            "company_infos_summary": company_infos_summary,
            "applicant_answer": applicant_answer,
            "interviewer_question": interviewer_question,  # 지원자가 받은 질문
            "available_personas_json": available_personas_for_tool,  # 페르소나 할당 도구가 이 정보를 참조할 수 있도록
        }

        # Agent Executor를 호출합니다.
        # `input` 키에 사용자 쿼리가 들어가고, 나머지 정보는 LLM이 판단하여 도구 인자로 활용합니다.
        # LLM이 도구 인자로 JSON을 생성하도록 유도하는 것은 프롬프트의 역할이 중요합니다.
        try:
            # invoke 호출 시 모든 관련 맥락 정보를 전달
            # Agent의 프롬프트와 도구 설명이 이 정보를 바탕으로 적절한 도구를 선택하도록 안내해야 합니다.
            # 예를 들어, user_query에 "페르소나 할당"과 같은 키워드가 있거나,
            # applicant_answer가 제공되면 "평가/모범 답변 생성" 도구를 사용하도록 유도합니다.
            full_input_to_agent = {
                "input": user_query,  # 주 사용자 쿼리
                "context_json": json.dumps(
                    context_for_agent_input, ensure_ascii=False
                ),  # Agent가 참조할 전체 맥락
            }

            # AgentExecutor.ainvoke를 호출합니다.
            result = await self.agent_executor.ainvoke(full_input_to_agent)

            # AgentExecutor의 결과는 딕셔너리 형태로 반환되며, 최종 답변은 'output' 키에 있습니다.
            final_answer = result.get("output", "Agent가 답변을 생성하지 못했습니다.")
            return final_answer
        except Exception as e:
            print(f"Agent 호출 중 오류 발생: {e}")
            return "죄송합니다, 요청을 처리하는 중 오류가 발생했습니다."
