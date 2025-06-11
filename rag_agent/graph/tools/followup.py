from langchain_core.tools import tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from config import llm

@tool
def generate_followup_reasoning(input_text):
    """지원자의 답변에 대한 꼬리질문 생성을 위해 지원자 답변 및 이전 대화내용을 기반으로 꼬리질문 이유(Reasoning) 도출"""
    
    reasoning_prompt = PromptTemplate.from_template(
        """
        아래는 AI 면접 시스템에서 지금까지 진행된 질문과 지원자의 답변입니다:

        대화 이력:
        {chat_history}

        현재 질문에 대한 지원자의 답변은 다음과 같습니다:
        "{input_text}"

        이 답변을 바탕으로 다음 꼬리질문을 이어가려는 면접관의 Reasoning을 작성하세요.
        예를 들어, 지원자의 말 중 구체적이지 않은 부분을 짚거나, 경험의 진정성, 추가 설명이 필요한 포인트를 찾아내세요.
        """
    )
    
    chain = reasoning_prompt | llm | StrOutputParser()
    return chain.invoke({
    })
    
@tool
def generate_followup_acting(reasoning, input_text):
    """Reasoning과 사용자의 답변을 기반으로 꼬리질문 생성"""

    prompt = PromptTemplate.from_template(
        """
        아래는 지원자의 답변과 그에 대한 면접관의 추론(Reasoning)입니다.

        [지원자 답변]
        {input_text}

        [면접관의 Reasoning]
        {reasoning}

        위 Reasoning을 바탕으로 다음 꼬리질문을 작성하세요.
        질문은 면접에서 실제로 사용할 수 있도록 자연스럽고 구체적으로 표현하세요.
        한 문장으로 작성하세요.
        """
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "reasoning": reasoning,
        "input_text": input_text
    })