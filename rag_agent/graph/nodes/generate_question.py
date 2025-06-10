from langchain_core.runnables import RunnableLambda
from tools import generate_question_reasoning, generate_question_acting

question_reasoning_node = RunnableLambda(lambda state: {
    **state,
    "reasoning": generate_question_reasoning.invoke({
        "resume": state["resume"],
        "jd": state["jd"],
        "company": state["company"]
    })
})

question_acting_node = RunnableLambda(lambda state: {
    **state,
    "final_answer": generate_question_acting.invoke({"reasoning": state["reasoning"]})
})
