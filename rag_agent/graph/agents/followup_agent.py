from langgraph.graph import StateGraph, END
from nodes import evaluate_answer_node, followup_reasoning_node, followup_acting_node

builder = StateGraph()
builder.add_node("evaluate_answer", evaluate_answer_node)
builder.add_node("followup_reasoning", followup_reasoning_node)
builder.add_node("followup_question", followup_acting_node)

builder.set_entry_point("evaluate_answer")
builder.add_edge("evaluate_answer", "followup_reasoning")
builder.add_edge("followup_reasoning", "followup_question")
builder.set_finish_point("followup_question")

followup_agent = builder.compile()
