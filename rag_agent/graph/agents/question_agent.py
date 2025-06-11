from langgraph.graph import StateGraph, END
from nodes import question_reasoning_node, question_acting_node

builder = StateGraph()
builder.add_node("generate_reasoning", question_reasoning_node)
builder.add_node("generate_question", question_acting_node)

builder.set_entry_point("generate_reasoning")
builder.add_edge("generate_reasoning", "generate_question")
builder.set_finish_point("generate_question")

question_agent = builder.compile()
