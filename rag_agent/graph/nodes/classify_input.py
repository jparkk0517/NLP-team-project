from langchain_core.runnables import RunnableLambda
from tools import classify_input

classify_input_node = RunnableLambda(lambda state: {
    **state,
    "classification": classify_input.invoke({"input": state["input"]})
})
