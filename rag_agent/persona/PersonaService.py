from typing import List, Optional, Self
from pydantic import BaseModel, Field

from ..chat_history.ChatHistory import ChatHistory
from ..chat_history.Singleton import Singleton

# rag_agent.chat_history.ChatHistory는 이 예제에서 직접 사용되지 않지만, 필요시 통합 가능
# from rag_agent.chat_history.ChatHistory import ChatHistory
from .Persona import Persona, PersonaType, llm  # Persona 클래스와 LLM 임포트
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

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


class PersonaInput(BaseModel):
    type: PersonaType
    name: str
    interests: Optional[list[str]] = None
    communicationStyle: Optional[str] = None


# --- Agent 구축 ---
# 1. Agent가 사용할 도구들을 정의합니다.
# 이 도구들은 위에서 정의한 `@tool` 함수들입니다.
tools = [
    # 필요시 다른 도구 추가
]

# 2. ReAct Agent를 생성합니다.
# create_react_agent는 LLM, 도구들, 프롬프트 템플릿을 받아 Agent 체인을 생성합니다.
agent = create_react_agent(llm, tools, AGENT_BASE_PROMPT)

# 3. AgentExecutor를 생성합니다.
# AgentExecutor는 Agent를 실행하고, 도구 실행 루프를 관리합니다.
# verbose=True로 설정하면 Agent의 Thought/Action/Observation 과정을 콘솔에 출력합니다.
# handle_parsing_errors=True는 LLM이 유효하지 않은 Action/Action Input을 생성했을 때 처리합니다.
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,  # 파싱 에러 발생 시 처리
    # memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True) # 다중 턴 대화 시
)


class PersonaService(Singleton):
    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.persona_list: List[Persona] = []

    def add_persona(self, persona: PersonaInput):
        new_persona = Persona(
            type=persona.type,
            name=persona.name,
            interests=persona.interests,
            communication_style=persona.communicationStyle,
        )
        self.persona_list.append(new_persona)
        return new_persona

    def get_persona_list(self) -> List[Persona]:
        return self.persona_list

    def delete_persona(self, persona_id: str):
        self.persona_list = [p for p in self.persona_list if p.id != persona_id]

    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        for persona in self.persona_list:
            if persona.id == persona_id:
                return persona
        return None
    
    def get_persona_str_by_id(self, persona_id: str) -> Optional[str]:
        for persona in self.persona_list:
            if persona.id == persona_id:
                return json.dumps(persona.get_persona_info(), ensure_ascii=False)
        return None

    def get_all_persona_info(self) -> str:
        return [p.get_persona_info() if p else None for p in self.persona_list]
    
    def invoke_agent(
        self,
        resume: str,
        jd: str,
        company_infos: Optional[str] = None,
        applicant_answer: Optional[str] = None,
        interviewer_question: Optional[str] = None,  # 지원자가 받은 질문
    ) -> str:
        available_personas_json = [p.get_persona_info() for p in self.persona_list]
        print("available_personas_json", available_personas_json)
        template = PromptTemplate(
            template="""     
You are an AI agent responsible for selecting the most appropriate persona for a job applicant based on the provided context.

Instructions:
- Analyze the applicant's resume, job description (JD) and applicant's interview answer.
- Evaluate all available personas.
- Select the single most appropriate persona based on similarity of interests, communication style, and role type.
- From the provided persona list, choose the single most appropriate **persona ID**.
- Do not explain your reasoning unless asked.
- Return ONLY the selected persona's ID in the format: Action Input: <persona_id>

---
resume:
{resume}

job description:
{jd}

applicant's interview response or input:
{applicant_answer}

available_personas_json: 
{available_personas_json}
            
---
You must follow the process below exactly:

Thought: your internal reasoning 
Final Answer: persona_id (or null if no persona is available)       

You must always end your response with a valid Final Answer.
Failure to do so will cause the system to fail.
Do not respond with "I don't know" or "I can't answer that". Always choose the best matching persona from the list.
ONLY return the <persona_id> as output.

Follow the Output Format:
<persona_id>

---

Begin:

Question: What is the ID of the most appropriate persona for this applicant?
            """,
            input_variables=[
                "resume",
                "jd",
                "applicant_answer",
                "available_personas_json",
            ],
        )
        chain = template | llm | StrOutputParser()
        return chain.invoke(
            {
                "resume": resume,
                "jd": jd,
                "applicant_answer": applicant_answer,
                "available_personas_json": available_personas_json,
                "interviewer_question": interviewer_question,
            }
        )