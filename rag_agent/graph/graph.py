from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from nodes import (
    classify_input_node,
    question_reasoning_node,
    question_acting_node,
    evaluate_answer_node,
    followup_reasoning_node,
    followup_acting_node
)
from routing import route_by_classification, route_by_evaluation  
from utils.ChatHistory import ChatHistory

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("langchain").setLevel(logging.DEBUG)

class AgentState(TypedDict):
    input: str
    resume: str
    jd: str
    company: str
    chat_history: ChatHistory
    last_question: str
    # messages: list[Annotated[AnyMessage, add_messages]] # LangGraph 내부 자동 메시지 관리

# 상태 그래프 정의
graph = StateGraph(AgentState)

# 노드 추가
graph.add_node("classify_input", classify_input_node)
graph.add_node("generate_question_reasoning", question_reasoning_node)
graph.add_node("generate_question_acting", question_acting_node)
graph.add_node("evaluate_answer", evaluate_answer_node)
graph.add_node("generate_followup_reasoning", followup_reasoning_node)
graph.add_node("generate_followup_acting", followup_acting_node)

# 분기 설정
graph.set_entry_point("classify_input")
graph.add_conditional_edges("classify_input", route_by_classification)

graph.add_edge("generate_question_reasoning", "generate_question_acting")
graph.add_edge("generate_question_acting", END)

graph.add_conditional_edges("evaluate_answer", route_by_evaluation)
graph.add_edge("generate_followup_reasoning", "generate_followup_acting")
graph.add_edge("generate_followup_acting", END)

# 컴파일
interview_graph = graph.compile()

print(interview_graph.get_graph().draw_mermaid())