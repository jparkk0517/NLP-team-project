from langchain_core.runnables import RunnableLambda
from tools import generate_followup_reasoning, generate_followup_acting

followup_reasoning_node = RunnableLambda(lambda state: {
    **state,
    "reasoning": generate_followup_reasoning.invoke({
        "answer": state["input"],
        "evaluation": state["evaluation"],
        "history": state["chat_history"],
        "question": state["last_question"]
    })
})

followup_acting_node = RunnableLambda(lambda state: {
    **state,
    "final_answer": generate_followup_acting.invoke({"reasoning": state["reasoning"]})
})
