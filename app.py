from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

import json
import os
import io
import shutil

from rag_agent import (
    ChatHistory,
    get_assessment_chain,
    get_evaluate_chain,
    get_followup_chain,
    get_interview_chain,
    get_model_answer_chain,
    get_initial_message_chain,
    get_reranking_model_answer_chain,
    compare_model_answers,
    agent_executor,
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Interview Simulator")
dist_path = os.path.join(os.path.dirname(__file__), "frontend/dist")

# 메모리 컨텍스트 저장 변수
stored_resume: Optional[str] = None
stored_jd: Optional[str] = None
# 사전 계산된 회사 정보 및 체인 저장 변수
stored_company_info: Optional[str] = None
init_message_chain = None
interview_chain = None
followup_chain = None
evaluate_chain = None
model_answer_chain = None
assessment_chain = None
base_chain_inputs: Optional[dict] = None
# RAG 벡터 스토어
vectorstore: Optional[Chroma] = None
# 영속 디렉토리 설정 (환경변수 또는 기본 경로)
persist_directory = os.getenv(
    "CHROMA_DB_PATH",
    os.path.join(os.path.dirname(__file__), "rag_agent/vectorstore/chroma_db"),
)


class AnswerRequest(BaseModel):
    questionId: str
    content: str


class Question(BaseModel):
    id: str
    content: str


class Answer(BaseModel):
    id: str
    content: str


chat_history = ChatHistory()


# 로컬 파일 시스템에서 context와 회사 자료 자동 로딩
# TODO: RAG PyPDF2 -> langchain vector db
def parse_file_to_text(file_path: str) -> str:
    with open(file_path, "rb") as f:
        content = f.read()
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        if file_path.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            return "\n".join(doc.page_content for doc in docs)
        elif file_path.lower().endswith((".docx", ".doc", ".txt")):
            loader = TextLoader(file_path)
            docs = loader.load()
            return "\n".join(doc.page_content for doc in docs)
        else:
            return content.decode("utf-8", errors="ignore")


async def init_local_data():
    """로컬 db를 모두 비운다"""
    global vectorstore
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
    os.makedirs(persist_directory, exist_ok=True)
    vectorstore = None
    logger.info("Vectorstore reset successfully.")


@app.on_event("startup")
async def load_local_data():
    await init_local_data()
    global stored_resume, stored_jd, vectorstore, stored_company_info, interview_chain, followup_chain, base_chain_inputs, chat_history, evaluate_chain, model_answer_chain, assessment_chain, init_message_chain, reranking_model_answer_chain
    base_dir = os.path.join(os.path.dirname(__file__), "data")
    # 이력서 로딩
    resume_dir = os.path.join(base_dir, "resume")
    for fname in os.listdir(resume_dir):
        stored_resume = parse_file_to_text(os.path.join(resume_dir, fname))
        break
    # JD 로딩
    jd_dir = os.path.join(base_dir, "jd")
    for fname in os.listdir(jd_dir):
        stored_jd = parse_file_to_text(os.path.join(jd_dir, fname))
        break
    # 회사 자료 로딩 및 인덱싱
    company_dir = os.path.join(base_dir, "company_infos")
    docs = []
    for fname in os.listdir(company_dir):
        text = parse_file_to_text(os.path.join(company_dir, fname))
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        for chunk in splitter.split_text(text):
            docs.append(Document(page_content=chunk, metadata={"filename": fname}))
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )
    if docs:
        texts = [d.page_content for d in docs]
        metadatas = [d.metadata for d in docs]
        vectorstore.add_texts(texts=texts, metadatas=metadatas)
        vectorstore.persist()
    logger.info("Loaded local resume, JD, and company infos.")
    # 사전 계산: 회사 정보와 체인 초기화
    stored_company_info = get_company_info()
    init_message_chain = get_initial_message_chain()
    interview_chain = get_interview_chain()
    followup_chain = get_followup_chain()
    evaluate_chain = get_evaluate_chain()
    model_answer_chain = get_model_answer_chain()
    assessment_chain = get_assessment_chain()
    reranking_model_answer_chain = get_reranking_model_answer_chain()
    base_chain_inputs = {
        "resume": stored_resume,
        "jd": stored_jd,
        "company_infos": stored_company_info,
    }
    logger.info("Precomputed company_info and initialized chains.")
    


def get_company_info():
    if vectorstore is None:
        raise HTTPException(
            status_code=400,
            detail="Company documents not uploaded. Please upload docs first.",
        )
    # 회사 자료 검색
    retrieved = vectorstore.similarity_search(stored_jd, k=3)
    company_info = "\n".join([doc.page_content for doc in retrieved])
    # Trim company_info to avoid exceeding model context window
    max_company_info_length = 2000
    if len(company_info) > max_company_info_length:
        company_info = company_info[:max_company_info_length]
    logger.info(f"Retrieved company info length: {len(company_info)}")
    return company_info


@app.get("/chatHistory")
async def get_chat_history():
    if not chat_history.history:
        try:
            if init_message_chain is None:
                raise HTTPException(
                    status_code=500, detail="Initial message chain not initialized."
                )
            logger.info("No chat history found. Generating initial message...")
            response = init_message_chain.invoke({})
            print(response)
            logger.info("Chain invocation completed")
            
            chat_history.add(
                type="question", speaker="agent", content=response["result"]
            )
            return chat_history.get_all_history()
        except Exception as e:
            logger.error(f"Error in question generation: {str(e)}")
    return chat_history.get_all_history()


@app.get("/question")
async def generate_question():
    try:
        if interview_chain is None or base_chain_inputs is None:
            raise HTTPException(
                status_code=500, detail="Interview chain not initialized."
            )
        logger.info("Generating question using pre-initialized chain")
        response = interview_chain.invoke(base_chain_inputs)
        logger.info("Chain invocation completed")

        question_id = chat_history.add(
            type="question", speaker="agent", content=response["result"]
        )
        return {
            "id": question_id,
            "content": response["result"],
        }
    except Exception as e:
        logger.error(f"Error in question generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/answer")
async def submit_answer(request: AnswerRequest):
    question_id = request.questionId
    content = request.content
    if not chat_history.validate_question_exists(question_id):
        raise HTTPException(status_code=404, detail="Cannot find question id.")

    answer_id = chat_history.add(
        type="answer",
        speaker="user",
        content=content,
        related_chatting_id=question_id,
    )
    """
    답변 평가 await 
    """
    evaluate_content = evaluate_chain.invoke(
        {
            **base_chain_inputs,
            "prev_question_answer_pairs": [
                {
                    "question": chat_history.get_question_by_id(question_id),
                    "answer": content,
                }
            ],
        }
    )

    chat_history.add(
        type="evaluate",
        speaker="agent",
        content=evaluate_content,
    )
    return {"id": answer_id, "content": content}


@app.get("/assessment")
async def get_assessment():
    """
    평가 결과 반환
    논리성, 직무적합성, 핵심가치 부합성, 커뮤니케이션 능력
    """
    assessment_content = assessment_chain.invoke(
        {
            **base_chain_inputs,
            "chat_history": chat_history.get_all_history_as_string(),
        }
    )
    return assessment_content


@app.get("/followUp")
async def generate_followup(questionId: str):
    question_id = questionId
    if chat_history.history is None:
        raise HTTPException(status_code=400, detail="No chat history yet.")
    if not chat_history.validate_question_exists(question_id):
        raise HTTPException(status_code=404, detail="Cannot find question id.")

    try:
        logger.info("Generating followup using pre-initialized chain")
        if followup_chain is None or base_chain_inputs is None:
            raise HTTPException(
                status_code=500, detail="Followup chain not initialized."
            )

        answer_item = chat_history.get_answer_by_question_id(question_id)
        chat_history_every_related = (
            chat_history.get_chat_history_every_related_by_chatting_id(question_id)
        )
        if len(chat_history_every_related) == 0:
            raise HTTPException(
                status_code=400, detail="No chat history every related by chatting id."
            )

        inputs = {
            **base_chain_inputs,
            "prev_question_answer_pairs": list(
                map(
                    lambda x: {
                        "type": x.type,
                        "speaker": x.speaker,
                        "content": x.content,
                    },
                    chat_history_every_related,
                )
            ),
        }

        response = followup_chain.invoke(inputs)
        question_id = chat_history.add(
            type="question",
            speaker="agent",
            content=response,
            related_chatting_id=answer_item.id,
        )
        logger.info("Followup generated")
        return {
            "id": question_id,
            "content": response,
        }
    except Exception as e:
        logger.error(f"Error in followup generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/modelAnswer")
async def generate_model_answer(questionId: str):
    try:
        question_item = chat_history.get_question_by_id(questionId)
        if not question_item:
            raise HTTPException(status_code=404, detail="Question not found.")
        
        response = model_answer_chain.invoke(
            {
                **base_chain_inputs,
                "question": question_item.content
            }
        )
        answer_id = chat_history.add(
            type="modelAnswer",
            speaker="agent",
            content=response["result"],
            related_chatting_id=questionId  # 질문 ID를 related_chatting_id로 설정
        )
        return {"id": answer_id, "content": response["result"]}
    except Exception as e:
        logger.error(f"Error in model answer generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/")
async def analyze_input(text: str):
    try:
        resume = base_chain_inputs["resume"]
        jd = base_chain_inputs["jd"]
        company = base_chain_inputs["company_infos"]

        input_text = f"""
        먼저 이 입력이 어떤 유형인지 판단합니다.
        입력: '{resume}'

        Action: classify_input
        Action Input: '{resume}'
        Observation: 입력 유형에 따라 분기 처리합니다.
        
        - 입력이 자소서(resume)인 경우:
            Action: generate_question_reasoning
            Action Input: {json.dumps({
                "resume": resume,
                "jd": jd,
                "company": company
            })}

            Action: generate_question_acting
            Action Input: '{{reasoning}}'

        - 입력이 면접답변(interview_answer)인 경우:
            Action: evaluate_answer
            Action Input: {json.dumps({
                "resume": resume,
                "jd": jd,
                "company": company
            })}
            
            Action: generate_acting
            Action Input: '{{reasoning}}'

        - 입력이 일반 텍스트(other)인 경우:
            Action: translate_to_korean
            Action Input: '{resume}'
            
            Action: generate_acting
            Action Input: '{{reasoning}}'

        Thought: 최종 결과 도출 완료
        Final Answer:
        """
        response = agent_executor.invoke({"input": input_text})
        question_id = chat_history.add(
            type="question", speaker="agent", content=response["output"]
        )
        return {
            "id": question_id,
            "content": response["output"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rerankedModelAnswer")
async def generate_reranked_model_answer(questionId: str):
    try:
        question_item = chat_history.get_question_by_id(questionId)
        if not question_item:
            raise HTTPException(status_code=404, detail="Question not found.")
        
        # 이전 질문/답변 쌍들 가져오기
        prev_pairs = []
        for item in chat_history.history:
            if item.type == "question" and item.related_chatting_id:
                answer = next((a for a in chat_history.history if a.id == item.related_chatting_id), None)
                if answer:
                    prev_pairs.append({
                        "question": item.content,
                        "answer": answer.content
                    })

        # 원본 모델 답변 가져오기
        original_answer = next(
            (item for item in chat_history.history if item.type == "modelAnswer" and item.related_chatting_id == questionId),
            None
        )
        if not original_answer:
            raise HTTPException(status_code=404, detail="Original model answer not found.")

        # reranking 답변 3개 생성
        reranked_responses = []
        for _ in range(3):
            response = reranking_model_answer_chain.invoke(
                {
                    **base_chain_inputs,
                    "question": question_item.content,
                    "prev_question_answer_pairs": prev_pairs
                }
            )
            reranked_responses.append(response["result"])

        # 각 답변을 원본과 비교하여 점수 계산
        best_score = -1
        best_answer = None
        for answer in reranked_responses:
            comparison = compare_model_answers(original_answer.content, answer)
            score = comparison["overall"]["reranked_total"]
            if score > best_score:
                best_score = score
                best_answer = answer

        answer_id = chat_history.add(
            type="rerankedModelAnswer",
            speaker="agent",
            content=best_answer,
            related_chatting_id=questionId
        )
        return {"id": answer_id, "content": best_answer}
    except Exception as e:
        logger.error(f"Error in reranked model answer generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compareModelAnswers")
async def compare_answers(questionId: str):
    try:
        # 디버깅을 위한 로깅 추가
        logger.info(f"Searching for answers related to questionId: {questionId}")
        logger.info(f"Current chat history: {[{'type': item.type, 'id': item.id, 'related_id': item.related_chatting_id} for item in chat_history.history]}")
        
        # 원본 모델 답변 가져오기
        original_answer = None
        for item in chat_history.history:
            if item.type == "modelAnswer" and item.related_chatting_id == questionId:
                original_answer = item
                logger.info(f"Found original answer with id: {item.id}")
                break
        
        if not original_answer:
            logger.error(f"Original model answer not found for questionId: {questionId}")
            raise HTTPException(status_code=404, detail="Original model answer not found. Please generate a model answer first using /modelAnswer endpoint.")

        # Reranking된 모델 답변 가져오기
        reranked_answer = None
        for item in chat_history.history:
            if item.type == "rerankedModelAnswer" and item.related_chatting_id == questionId:
                reranked_answer = item
                logger.info(f"Found reranked answer with id: {item.id}")
                break

        if not reranked_answer:
            logger.error(f"Reranked model answer not found for questionId: {questionId}")
            raise HTTPException(status_code=404, detail="Reranked model answer not found. Please generate a reranked answer first using /rerankedModelAnswer endpoint.")

        # 답변 비교
        logger.info("Comparing answers...")
        comparison_result = compare_model_answers(
            original_answer.content,
            reranked_answer.content
        )
        logger.info("Comparison completed successfully")

        return comparison_result
    except Exception as e:
        logger.error(f"Error in comparing model answers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
