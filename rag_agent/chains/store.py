import os
import shutil
import logging
from typing import Optional

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

logger = logging.getLogger(__name__)

# RAG 벡터 스토어
vectorstore: Optional[Chroma] = None
vectorstore_retriever = None

# 영속 디렉토리 경로
persist_directory = os.getenv(
    "CHROMA_DB_PATH",
    os.path.join(os.path.dirname(__file__), "rag_agent/vectorstore/chroma_db"),
)

# 프로젝트 루트 기준으로 base_dir 정의
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # => NLP-team-project
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
COMPANY_INFO_DIR = os.path.join(DATA_DIR, "company_infos")

def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        raise ValueError("vectorstore has not been initialized yet.")
    return vectorstore

def get_vectorstore_retriever():
    global vectorstore_retriever
    if vectorstore_retriever is None:
        raise ValueError("vectorstore_retriever has not been initialized yet.")
    return vectorstore_retriever

# 로컬 파일 시스템에서 context와 회사 자료 자동 로딩
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

def reset_vectorstore():
    global vectorstore
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
    os.makedirs(persist_directory, exist_ok=True)
    vectorstore = None
    logger.info("Vectorstore reset successfully.")

def load_vectorstore_from_company_infos():
    global vectorstore, vectorstore_retriever
    base_dir = os.path.join(os.path.dirname(__file__), "data")
    
    # 회사 자료 로딩 및 인덱싱
    docs = []
    for fname in os.listdir(COMPANY_INFO_DIR):
        text = parse_file_to_text(os.path.join(COMPANY_INFO_DIR, fname))
        splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=50)
        for chunk in splitter.split_text(text):
            docs.append(Document(page_content=chunk, metadata={"filename": fname}))

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )
    vectorstore_retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

    if docs:
        texts = [d.page_content for d in docs]
        metadatas = [d.metadata for d in docs]
        vectorstore.add_texts(texts=texts, metadatas=metadatas)
        vectorstore.persist()
        logger.info("Vectorstore loaded and persisted from company_infos.")

    return vectorstore
