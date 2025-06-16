import os
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_community.tools import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from langgraph.graph import START, END, StateGraph

from rag_agent import ChatHistory
from ..persona.PersonaService import PersonaService
from rag_agent.chains.store import get_vectorstore_retriever, get_vectorstore

from IPython.display import Image, display

load_dotenv()


class Route(BaseModel):
    target: Literal["question", "evaluate", "modelAnswer", "followup", "other"] = Field(
        description="The target for the query to answer"
    )

class AgentState(TypedDict):
    query: str  # 사용자 답변
    answer: str  # Agent 답변
    input_type: str  # 사용자 답변 유형
    persona_id: str  # 페르소나 ID
    selected_persona: str # 페르소나 내용
    persona_list: list # 가용 페르소나 리스트트
    route_type: str  # routing 결과
    resume: str  # 자소서(이력서)
    jd: str  # 채용공고
    company: str  # 회사정보 (인재상)
    company_query: str # 회사정보 검색을 위한 질문
    chat_history: ChatHistory  # 대화내역
    last_question: str  # 마지막 질문


llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model_name="gpt-4o-mini"
)


def get_company_info(query):
    # if vectorstore is None:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Company documents not uploaded. Please upload docs first.",
    #     )
    # 회사 자료 검색
    vectorstore = get_vectorstore()
    retrieved = vectorstore.similarity_search(query, k=3)
    company_info = "\n".join([doc.page_content for doc in retrieved])
    # Trim company_info to avoid exceeding model context window
    max_company_info_length = 2000
    if len(company_info) > max_company_info_length:
        company_info = company_info[:max_company_info_length]
    return company_info

doc_relevance_prompt = hub.pull("langchain-ai/rag-document-relevance")

tavily_search_tool = TavilySearchResults(
    max_results=3,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=False,
)

def retrieve(state: AgentState) -> AgentState:
    """
    사용자의 질문에 기반하여 벡터 스토어에서 관련 문서를 검색합니다.

    Args:
        state (AgentState): 사용자의 질문을 포함한 에이전트의 현재 state.

    Returns:
        AgentState: 검색된 문서가 추가된 state를 반환합니다.
    """
    jd = state.get("jd", "")
    company = state.get("company", "")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(company)
    
    if not company or company is None:
        docs = get_company_info(jd)
        if docs is not None:
            doc_relevance_chain = doc_relevance_prompt | llm
            response = doc_relevance_chain.invoke({'question': jd, 'documents': docs})
            print("doc_relevance_chain >", response['Score'])
            
            if response['Score'] == 1:
                return {'company': docs}
        
        rewrite_prompt = PromptTemplate.from_template(
"""사용자의 입력은 채용공고입니다. 내용을 확인하고 해당 기업의 회사정보, 인재상에 대한 웹 검색이 용이하도록 사용자의 질문을 50자 이내 자연어로 작성해주세요.

조건:
- 해당 기업 공식사이트에서 정확한 정보를 가져올 수 있도록 유도
- 물음표(?)로 끝나는 질문이 아닌 검색이 용이한 키워드 형태로 출력
- 예시: "삼성 채용 사이트에서 인재상" 또는 "네이버 인재상 site:recruit.navercorp.com"

질문: 
{query}""")

        rewrite_chain = rewrite_prompt | llm | StrOutputParser()

        company_query = rewrite_chain.invoke({'query': jd})
        print("web_search query > ", company_query)
        results = tavily_search_tool.invoke({ "query": company_query })
        contents = [item.get("content", "") for item in results]
        print("***********************************************************************")
        print(contents)
        return {"company": contents}
    else:
        return {"company": company}

def check_doc_relevance(state: AgentState) -> Literal['relevant', 'irrelvant']:
    """
    주어진 state를 기반으로 문서의 관련성을 판단합니다.

    Args:
        state (AgentState): 사용자의 질문과 문맥을 포함한 에이전트의 현재 state.

    Returns:
        Literal['relevant', 'irrelevant']: 문서가 관련성이 높으면 'relevant', 그렇지 않으면 'irrelevant'를 반환합니다.
    """
    query = state.get("jd", "")
    context = state.get("company", "")
  
    doc_relevance_chain = doc_relevance_prompt | llm
    response = doc_relevance_chain.invoke({'question': query, 'documents': context})
    print("doc_relevance_chain >", response['Score'])

    if response['Score'] == 1:
        return 'relevant'
    
    return 'irrelvant'

def rewrite(state: AgentState) -> AgentState:
    """
    사용자의 질문을 사전을 참고하여 변경합니다.

    Args:
        state (AgentState): 사용자의 질문을 포함한 에이전트의 현재 state.

    Returns:
        AgentState: 변경된 질문을 포함하는 state를 반환합니다.
    """
    rewrite_prompt = PromptTemplate.from_template("""사용자의 입력은 채용공고입니다. 내용을 확인하고 해당 기업의 회사정보, 인재상에 대한 웹 검색이 용이하도록 사용자의 질문을 50자 이내 자연어로 작성해주세요.
조건:
- 해당 기업 공식사이트에서 정확한 정보를 가져올 수 있도록 유도
- 물음표(?)로 끝나는 질문이 아닌 검색이 용이한 키워드 형태로 출력
- 예시: "삼성 채용 사이트에서 인재상" 또는 "네이버 인재상 site:recruit.navercorp.com"

질문: 
{query}""")

    query = state.get("jd", "")
    rewrite_chain = rewrite_prompt | llm | StrOutputParser()

    response = rewrite_chain.invoke({'query': query})
    return {'company_query': response}


def web_search(state: AgentState) -> AgentState:
    """
    주어진 state를 기반으로 웹 검색을 수행합니다.

    Args:
        state (AgentState): 사용자의 질문을 포함한 에이전트의 현재 state.

    Returns:
        AgentState: 웹 검색 결과가 추가된 state를 반환합니다.
    """
    try:
        query = state.get("company_query", "")
        print("web_search query > ", query)
        results = tavily_search_tool.invoke({ "query": query })
        contents = [item.get("content", "") for item in results]
        print("***********************************************************************")
        print(contents)
        return {"company": contents}
    except Exception as e:
        print(str(e))
        return {
            "error": f"web_search 노드에서 오류 발생: {str(e)}",
            "status": "error",
            "messages": state.get("messages", []) + [
                {"role": "system", "content": f"오류: {str(e)}"}
            ],
        }


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
    chat_history = state.get("chat_history", "")
    print("classify_input > query >", query)

    classify_prompt = PromptTemplate.from_template(
        """
주어진 입력과 대화 내역을 바탕으로 입력이 어떤 유형인지 판단하세요: 
- 면접질문 요청 (question)
- 꼬리질문 요청 (followup)
- 모범답변 요청 (modelAnswer)
- 지원자의 면접 답변 (response)
- 평가 요청 (evaluate)
- 그 외 면접과 관련 없는 텍스트 (other)


사용자 입력:
{query}

대화 내역:
{chat_history}

형식: question, followup, modelAnswer, response, evaluate, other 중 하나로만 답하세요."""
    )

    router_chain = classify_prompt | llm | StrOutputParser()
    result = router_chain.invoke({"query": query, "chat_history": chat_history})

    print("classify_input > result >", result)
    
    

    # 결과 메시지를 업데이트하고 router node로 이동합니다.
    return {"input_type": result}


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
    
    if persona_id:
        persona_info = persona_service.get_persona_str_by_id(persona_id)
    
    persona_list = persona_service.get_all_persona_info()

    return {"persona_id": persona_id, "persona_list": persona_list, "selected_persona": persona_info }


def router(state: AgentState) -> AgentState:
    """
    주어진 state에서 input_type를 기반으로 적절한 경로를 결정합니다.

    Args:
        state (AgentState): 현재 에이전트의 state를 나타내는 객체입니다.

    Returns:
        Literal["question", "evaluate", "modelAnswer", "followup", "other"]: 쿼리에 따라 선택된 경로를 반환합니다.
    """

    query = state["input_type"]
    router_system_prompt = """
You are an expert at routing a user's input type to one of the following:
- 'question'
- 'modelAnswer'
- 'evaluate'
- 'followup'
- 'other'

Instructions:
- If the input is exactly 'question', return 'question'.
- If the input is exactly 'response' or exactly 'evaluate', return 'evaluate'.
- If the input is exactly 'followup', return 'followup'.
- If the input is exactly 'modelAnswer', return 'modelAnswer'.
- Otherwise, return 'other'.

Note:
- 'response' means a user's response to an interview question.
- 'evaluate' refers to evaluating that answer.
Both should be routed to 'evaluate'.

Only return one of: 'question', 'evaluate', 'followup', 'modelAnswer', 'other'."""

    router_prompt = ChatPromptTemplate.from_messages(
        [("system", router_system_prompt), ("user", "{query}")]
    )

    structured_router_llm = llm.with_structured_output(Route)

    router_chain = router_prompt | structured_router_llm
    route = router_chain.invoke({"query": query})
    print("router", route)

    return {"route_type": route.target}


def generation(state: AgentState) -> AgentState:
    """
    사용자 입력과, 이전 대화내용을 바탕으로 면접 질문을 생성하고,
    결과를 전달합니다.

    Args:
        state (MessageState): 현재 메시지 상태를 나타내는 객체입니다.

    Returns:
        Command: 생성한 면접 질문을 반환합니다.
    """
    try:
        # 상태에서 필요한 정보 추출
        resume = state.get("resume", "")
        jd = state.get("jd", "")
        company = state.get("company", "")
        selected_persona = state.get("selected_persona", "")

        generation_prompt = PromptTemplate.from_template(
            """다음은 지원자의 자소서, JD(직무기술서), 회사 정보, 그리고 면접관 페르소나입니다:

자기소개서:
{resume}

JD:
{jd}

회사 정보:
{company}

면접관 페르소나:
{selected_persona}

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

---
주의할 점:
- 반드시 2단계에서 생성된 질문(acting 결과)만 출력하세요.
- 1단계 Reasoning(분석) 내용은 절대 출력하지 마세요.
- 질문 이외의 설명, 분석, 안내 문구도 출력하지 마세요.
- "[질문]"이나 "면접 질문:" 같은 태그는 붙이지 마세요. 질문 문장만 출력하세요.

출력 예시:
복잡한 비즈니스 문제를 기술로 해결한 경험에 대해 말씀해 주시고, 그 과정에서 어떤 기술적 선택을 하셨는지, 결과에 어떤 영향을 미쳤는지 구체적으로 설명해 주시겠습니까?
"""
        )

        chain = generation_prompt | llm | StrOutputParser()
        result = chain.invoke(
            {"resume": resume, "jd": jd, "company": company, "selected_persona": selected_persona}
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
    결과를 전달합니다.

    Args:
      state (MessageState): 현재 메시지 상태를 나타내는 객체입니다.

    Returns:
      Command: 생성한 꼬리 면접 질문을 반환합니다.
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

주의할 점:
- 반드시 2단계에서 생성된 질문(acting 결과)만 출력하세요.
- 1단계 Reasoning(분석) 내용은 절대 출력하지 마세요.
- 질문 이외의 설명, 분석, 안내 문구도 출력하지 마세요.
- "[질문]"이나 "면접 질문:" 같은 태그는 붙이지 마세요. 질문 문장만 출력하세요.

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

def evaluate(state: AgentState) -> AgentState:
    """
    지원자의 답변과 대화 이력, 페르소나 정보를 바탕으로
    각 페르소나별 평가를 생성하고, 최종 평가 결과를 반환합니다.
    """
    try:
        resume = state.get("resume", "")
        jd = state.get("jd", "")
        company = state.get("company", "")
        chat_history = state.get("chat_history", "")
        persona_list = state.get("persona_list", "")
        last_question = state.get("last_question", "")
        answer = state.get("query", "")

        # 필수 정보 체크
        if not all([resume, jd, company, chat_history, persona_list, last_question, answer]):
            return {
                "error": "평가에 필요한 정보가 부족합니다.",
                "status": "error",
                "messages": state.get("messages", []) + [
                    {"role": "system", "content": "평가에 필요한 정보가 부족합니다."}
                ],
            }

        # 평가 프롬프트
        assessment_prompt = PromptTemplate(
            input_variables=["resume", "jd", "company", "question", "answer", "persona", "chat_history"],
            template="""
역할: 주어진 페르소나 리스트의 면접관들이 지원자의 답변을 평가하고, 그 결과를 합산합니다.

직무 설명:
{jd}

이력서:
{resume}

회사 정보:
{company}

면접 질문:
{question}

지원자 답변:
{answer}

대화 이력:
{chat_history}

면접관 리스트 정보(개별 평가):
{persona}

[1단계]
각 페르소나별로 다음 4개 항목을 0~10점으로 평가하세요:
1. 논리성 (logicScore)
2. 직무적합성 (jobFitScore)
3. 핵심가치 부합성 (coreValueFitScore)
4. 커뮤니케이션 능력 (communicationScore)

[2단계]
각 항목별 점수를 평균내고, 최종 코멘트를 200자 이내로 작성하세요.

[input_type: response 일때, 실제 출력]
    면접관이 위에서 생성된 4가지 항목을 종합하여 실제로 응답하는 형식으로 생성하세요.

    주의할 점:
    - 반드시 1단계 Reasoning(분석) 내용은 절대 출력하지 마세요.
    - 점수를 공개 하지 마세요.
    - 모든 페르소나 평가 결과를 점수를 제외하고 구어체 형식으로로 말해주세요.
    - 답변은 실제 면접관이 답변을 이어가는 형식으로 생성해야 한다.

------------------------------------------------------------------------------------------------

[input_type: evaluate 일때, 실제 출력]
    자연스럽게 면접관이 답변하는 형식으로 출력하세요. 점수는 공개하세요.

    주의할 점:
    - 이때는 4가지 항목에 대한 점수를 공개 하세요.
    - 개선점을 말해주세요.
    - 답변은 실제 면접관이 답변을 이어가는 형식으로 생성해야 한다.
"""
        )

        # 평가 실행
        parser = JsonOutputParser()
        chain = assessment_prompt | llm | StrOutputParser()
        result = chain.invoke({
            "resume": resume,
            "jd": jd,
            "company": company,
            "question": last_question,
            "answer": answer,
            "persona": persona_list,
            "chat_history": chat_history,
        })
        return {"answer": result}

    except Exception as e:
        return {
            "error": f"Evaluate 노드에서 오류 발생: {str(e)}",
            "status": "error",
            "messages": state.get("messages", []) + [
                {"role": "system", "content": f"오류: {str(e)}"}
            ],
        }
    

def modelAnswer(state: AgentState) -> AgentState:
    """
    STAR 기법 등 구조화된 최적의 모범 답변을 생성하는 LangGraph용 노드 함수.
    이력서, JD, 회사정보, 이전 Q&A, 질문, 페르소나 등 context를 모두 반영.
    """
    try:
        # 1. 상태에서 정보 추출
        resume = state.get("resume", "")
        jd = state.get("jd", "")
        company_infos = state.get("company", "")
        prev_question_answer_pairs = state.get("chat_history", "")
        question = state.get("last_question", "")
        persona = state.get("persona_id", "")
        chat_history = state.get("chat_history", "")

        # 2. 프롬프트 템플릿 정의
        prompt = PromptTemplate.from_template(
            """
아래는 AI 면접 시스템에서 지금까지 진행된 대화입니다:

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

면접관 페르소나:
{persona}

대화 이력:
{chat_history}

---
당신은 위 페르소나를 기반으로 하는 면접관입니다.
주어진 질문에 대해 최적의 답변을 생성해야 합니다.
이 답변은 회사의 가치관, 직무 요구사항, 그리고 이력서의 내용을 모두 고려해야 합니다.

[Reasoning]
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

[Acting] 
위에서 생성된 4가지 항목을 종합하여 면접자가 실제로 응답하는 형식으로 모범답변을 생성하세요.

주의할 점:
- 반드시 1단계 Reasoning(분석) 내용은 절대 출력하지 마세요.
- 답변은 한글로 생성해야 한다.
- 답변은 실제 면접자가 면접장에서 답변하는 형식으로 생성해야 한다.

**하지만, 아래의 조건을 반드시 지키세요:**
- Reasoning(분석) 단계의 내용을 절대 출력하지 마세요.
- 답변은 실제 면접자가 면접장에서 자연스럽게 말하는 것처럼 한글로 작성하세요.
- 항목별 분석이나 구조화된 리스트 형태가 아닌, 자연스러운 대화체로만 답변하세요.


[answer] 
[생성된 모범답변]
"""
        )

        # 3. LLM 체인 실행
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke(
            {
                "resume": resume,
                "jd": jd,
                "company_infos": company_infos,
                "prev_question_answer_pairs": prev_question_answer_pairs,
                "question": question,
                "persona": persona,
                "chat_history": chat_history,
            }
        )

        # 4. 결과를 state에 업데이트
        return {**state, "answer": result}

    except Exception as e:
        return {
            **state,
            "error": f"modelAnswer_node에서 오류 발생: {str(e)}",
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
    query = state["query"]
    llm_chain = llm | StrOutputParser()
    llm_answer = llm_chain.invoke(query)
    return {"answer": llm_answer}


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
    next_route = state.get("route_type", "other")

    # 그래프 노드 이름과 매핑
    route_mapping = {
        "question": "generation",
        "response": "evaluate",
        "evaluate": "evaluate",
        "followup": "followup",
        "modelAnswer": "modelAnswer",
        "other": "llm",
    }

    return route_mapping.get(next_route, "llm")


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
        graph_builder.add_node("retrieve", retrieve)
        graph_builder.add_node("classify_input", classify_input)
        graph_builder.add_node("assign_persona", assign_persona_node)
        
        graph_builder.add_node("router", router)
        graph_builder.add_node("generation", generation)
        graph_builder.add_node("followup", followup)
        graph_builder.add_node("evaluate", evaluate)
        graph_builder.add_node("llm", call_llm)
        graph_builder.add_node("modelAnswer", modelAnswer)

        # 시작점에서 병렬 실행
        graph_builder.add_edge(START, "retrieve")
        graph_builder.add_edge(START, "classify_input")
        graph_builder.add_edge(START, "assign_persona")

        # 두 병렬 노드가 완료되면 라우터로
        graph_builder.add_edge("retrieve", "router")
        graph_builder.add_edge("classify_input", "router")
        graph_builder.add_edge("assign_persona", "router")

        # 생성 노드에서 종료
        graph_builder.add_edge("generation", END)
        graph_builder.add_edge("followup", END)
        graph_builder.add_edge("evaluate", END)
        graph_builder.add_edge("llm", END)
        graph_builder.add_edge("modelAnswer", END)

        graph_builder.add_conditional_edges(
            "router",
            conditional_router,
            {
                "generation": "generation",
                "followup": "followup",
                "llm": "llm",
                "evaluate": "evaluate",
                "modelAnswer": "modelAnswer",
            },
        )
        
        self.graph = graph_builder.compile()
        display(Image(self.graph.get_graph().draw_mermaid_png()))
        
        with open("graph.png", "wb") as f:
            f.write(self.graph.get_graph().draw_mermaid_png())

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

'''
Tech Corp

About Us:
Tech Corp is a leading technology company specializing in artificial intelligence and machine learning solutions. We are committed to innovation and excellence in everything we do.

Culture:
- Collaborative and inclusive work environment
- Emphasis on continuous learning and growth
- Work-life balance
- Remote-friendly workplace

Benefits:
- Competitive salary
- Health insurance
- 401(k) matching
- Flexible work hours
- Professional development opportunities 

'''