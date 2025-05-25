from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings  # 수정된 import
import os

# 샘플 자소서
SAMPLE_RESUME = """
[자기소개서]
안녕하세요. 저는 3년차 백엔드 개발자입니다.
주요 기술 스택은 Python, Django, FastAPI입니다.
대규모 트래픽 처리를 위한 시스템 설계와 마이크로서비스 아키텍처 구축 경험이 있습니다.
최근에는 AI 기반 서비스 개발에 관심을 가지고 LangChain과 RAG 시스템을 연구하고 있습니다.
"""

# 샘플 JD
SAMPLE_JD = """
[직무 설명]
- AI 기반 서비스 개발 및 운영
- LangChain을 활용한 RAG 시스템 구축
- FastAPI 기반 백엔드 API 개발
- 대규모 트래픽 처리를 위한 시스템 설계 및 구현

[자격 요건]
- Python 개발 경력 3년 이상
- FastAPI 또는 Django 프레임워크 사용 경험
- AI/ML 관련 프로젝트 경험 우대
- 클라우드 환경(AWS/GCP) 사용 경험
"""


def create_and_store_documents():
    # 텍스트 분할기 초기화
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    # 문서 분할
    resume_chunks = text_splitter.split_text(SAMPLE_RESUME)
    jd_chunks = text_splitter.split_text(SAMPLE_JD)

    # 임베딩 모델 초기화
    embeddings = OpenAIEmbeddings()

    # 벡터스토어 초기화
    persist_directory = os.getenv("CHROMA_DB_PATH", "./rag_agent/vectorstore/chroma_db")
    vectordb = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )

    # 문서 저장
    vectordb.add_texts(resume_chunks + jd_chunks)
    vectordb.persist()

    print("샘플 문서가 벡터스토어에 저장되었습니다.")


if __name__ == "__main__":
    create_and_store_documents()
