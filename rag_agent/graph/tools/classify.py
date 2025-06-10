from langchain_core.tools import tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from config import llm

@tool
def classify_input(input):
    """입력이 자소서인지, 면접답변인지, 일반 텍스트인지 구분합니다."""
    classify_prompt = PromptTemplate.from_template(
        """
        다음 입력이 어떤 유형인지 판단하세요: 
        - 자소서 (resume)
        - 면접 질문에 대한 답변 (interview_answer)
        - 그 외 일반 텍스트 (other)

        입력:
        {input}

        형식: resume, interview_answer, other 중 하나로만 답하세요.
        """
    )
    chain = classify_prompt | llm | StrOutputParser()
    return chain.invoke({"input": input})
