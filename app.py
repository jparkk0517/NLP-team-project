from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Literal, Optional
import uvicorn
import logging
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

import json
import os
import shutil

from rag_agent import (
    ChatHistory,
    # get_evaluate_chain,
    # get_followup_chain,
    # get_interview_chain,
    # get_model_answer_chain,
    get_initial_message_chain,
    get_reranking_model_answer_chain,
    compare_model_answers,
    agent_executor,
    PersonaService,
)
from rag_agent.chains.interview_graph import GraphAgent
from rag_agent.persona.Persona import Persona, PersonaType
from rag_agent.persona.PersonaService import PersonaInput

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
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
agent = None

chat_history = ChatHistory.get_instance()

persona_service = PersonaService.get_instance()
print(ChatHistory.get_instance(), PersonaService.get_instance())


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
    global stored_resume, stored_jd, vectorstore, stored_company_info, interview_chain, followup_chain, base_chain_inputs, chat_history, evaluate_chain, model_answer_chain, assessment_chain, init_message_chain, reranking_model_answer_chain, agent
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
        splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=50)
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
    reranking_model_answer_chain = get_reranking_model_answer_chain()
    base_chain_inputs = {
        "resume": stored_resume,
        "jd": stored_jd,
        "company_infos": stored_company_info,
    }

    agent = GraphAgent(
        resume=stored_resume,
        jd=stored_jd,
        company=stored_company_info,
    )
    # 페르소나 추가 (테스트용)
    persona_service.add_persona(
        PersonaInput(
            name="Recruiter",
            type="other",
            interests=["조직 적응력", "인성"],
            communicationStyle="차분하고 상냥한 스타일",
        )
    )
    persona_service.add_persona(
        PersonaInput(
            name="CTO",
            type="developer",
            interests=["이슈 해결 과정과 Lessons Learned"],
            communicationStyle="불필요한 말은 하지 않음, 합리적이고 이성적인 스타일",
        )
    )
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


def search_query_by_vector(query: str) -> str:
    if vectorstore is None:
        raise HTTPException(
            status_code=400,
            detail="Company documents not uploaded. Please upload docs first.",
        )
    retrieved = vectorstore.similarity_search(query, k=3)


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
            logger.info("Chain invocation completed")

            chat_history.add(
                type="question", speaker="agent", content=response["result"]
            )
            return chat_history.get_all_history()
        except Exception as e:
            logger.error(f"Error in question generation: {str(e)}")
    return chat_history.get_all_history()


RequestType = Literal["question", "followup", "modelAnswer", "answer", "other"]


@app.get("/assessment")
async def get_assessment():
    """
    interface AssessmentResultDTO {
      logicScore: number;
      jobFitScore: number;
      coreValueFitScore: number;
      communicationScore: number;
      averageScore: number;
      overallEvaluation: string;
    }"""
    return {
        "logicScore": 4,
        "jobFitScore": 6,
        "coreValueFitScore": 5,
        "communicationScore": 5,
        "averageScore": 5,
        "overallEvaluation": """이 지원자는 해당 면접에 적합하지 않습니다. 논리성에서 낮은 점수를 받았고, 직무적합도는 높은 점수를 받았습니다. 하지만 핵심가치와 커뮤니케이션에서는 중간 점수를 받았습니다.
        결과적으로 해당 지원자는 면접결과 애매한 점수를 기록하여 합격하기에 적합하지 않습니다.
        """,
    }


class RequestInput(BaseModel):
    type: Optional[RequestType] = None
    content: str
    related_chatting_id: Optional[str] = None


@app.post("/")
async def analyze_input(request: RequestInput):
    type = request.type
    content = request.content
    related_chatting_id = request.related_chatting_id
    chat_history.add(type=type, speaker="user", content=content)
    try:
        resume = base_chain_inputs["resume"]
        jd = base_chain_inputs["jd"]
        company = base_chain_inputs["company_infos"]
        last_question = chat_history.get_question_by_id(
            chat_history.get_latest_question_id()
        )
        recent_history = chat_history.get_all_history_as_string()

        persona_id = persona_service.invoke_agent(
            resume=resume, jd=jd, applicant_answer=content
        )

        persona_info = ""
        if "null" not in persona_id:
            persona_info = persona_service.get_persona_str_by_id(persona_id)

        response = agent.run(content)

        # modelAnswer 타입일 때만 reranking 수행
        if type == "modelAnswer":
            original_answer = response.get("answer", "")

            # 이전 질문/답변 쌍들 가져오기
            prev_pairs = []
            for item in chat_history.history:
                if item.type == "question" and item.related_chatting_id:
                    answer = next(
                        (
                            a
                            for a in chat_history.history
                            if a.id == item.related_chatting_id
                        ),
                        None,
                    )
                    if answer:
                        prev_pairs.append(
                            {"question": item.content, "answer": answer.content}
                        )

            # reranking 답변 3개 생성
            reranked_responses = []
            for _ in range(3):
                reranked_response = reranking_model_answer_chain.invoke(
                    {
                        **base_chain_inputs,
                        "question": last_question.content if last_question else "",
                        "prev_question_answer_pairs": prev_pairs,
                    }
                )
                reranked_responses.append(reranked_response["result"])

            # 각 답변을 원본과 비교하여 점수 계산
            best_score = -1
            best_answer = original_answer
            for answer in reranked_responses:
                comparison = compare_model_answers(original_answer, answer)
                score = comparison["overall"]["reranked_total"]
                if score > best_score:
                    best_score = score
                    best_answer = answer

            # 최종 답변 저장
            chat_history.add(
                type="modelAnswer",
                speaker="agent",
                content=best_answer,
                related_chatting_id=related_chatting_id,
                persona_info=persona_info,
            )
        else:
            # reranking이 필요없는 경우 원본 응답 저장
            chat_history.add(
                type="question",
                speaker="agent",
                content=response.get("answer", ""),
                persona_info=persona_info,
            )

        return chat_history.get_all_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/persona/list")
async def get_persona_list():
    return persona_service.get_all_persona_info()


@app.post("/persona")
async def add_persona(persona: PersonaInput):
    try:
        new_persona = persona_service.add_persona(persona)
        return new_persona.get_persona_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/persona/{persona_id}")
async def delete_persona(persona_id: str):
    persona = persona_service.get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found.")
    persona_service.delete_persona(persona_id)
    return None


app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
