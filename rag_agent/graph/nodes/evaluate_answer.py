from langchain_core.runnables import RunnableLambda
from tools import generate_assessment_answer

evaluate_answer_node = RunnableLambda(lambda state: {
    **state,
    "evaluation": generate_assessment_answer.invoke({
        "data": {
            "resume": state["resume"],
            "jd": state["jd"],
            "company": state["company"],
            "answer": state["input"]
        }
    })
})
