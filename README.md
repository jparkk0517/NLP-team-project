# 🧑‍💼 AI Interview Simulator

**LangChain과 RAG 기반의 AI 면접 시뮬레이터**  
자소서·JD 기반 맞춤형 질문, 답변 평가, 꼬리질문/모범답변까지!  
실제 면접처럼 연습하고, AI로부터 피드백을 받아보세요.

---

## 🏗️ 프로젝트 개요

- **목표**: 사용자의 자소서, JD, 기업정보를 바탕으로 AI가 면접관 역할을 하여 질문을 생성하고, 답변을 평가하며, 꼬리질문·모범답변·다음질문을 제시하는 시뮬레이터 제공
- **핵심 기술**: LangChain, FastAPI, RAG, ChromaDB, React, TypeScript, Vite

---

## 🚀 주요 기능

- **맞춤형 면접 질문 생성**: 자소서·JD 기반 직무 맞춤형 질문
- **답변 평가**: 논리성·구체성·직무적합성 평가 및 개선 제안
- **꼬리질문/모범답변/다음질문**: 답변에 따라 다양한 후속 질문 및 예시 제공
- **채팅 기반 UI**: 실제 면접처럼 자연스러운 대화 흐름
- **(확장) 음성 답변(STT), 이력 저장 등**

---

## 🗂️ 폴더 구조

```text
📁 rag_agent/           # 백엔드(면접 로직, API)
│
├── app.py              # FastAPI 서버 진입점
├── chains/             # LangChain 체인(질문/평가/꼬리질문)
│   ├── interview_chain.py
│   ├── evaluate_chain.py
│   └── followup_chain.py
├── vectorstore/        # 임베딩 벡터 저장소(ChromaDB)
├── data/               # 자소서/JD 등 문서 저장
│
📁 frontend/            # 프론트엔드(React+Vite)
│   ├── src/            # 주요 소스코드
│   └── public/         # 정적 파일
│
📁 data/                # 데이터셋(예시)
```

---

## 🛠️ 기술 스택

- **백엔드**: Python, FastAPI, LangChain, ChromaDB, OpenAI/HuggingFace Embedding
- **프론트엔드**: React, TypeScript, Vite, TailwindCSS

---

## 📝 기획안 요약

- **문서 저장소**: 자소서/JD/기업정보를 벡터로 저장, RAG 기반 검색
- **질문 생성**: 프롬프트 기반 맞춤형 질문 생성
- **답변 평가**: 항목별 점수+개선 제안
- **후속질문/모범답변**: 답변에 따라 다양한 흐름 제공
- **API**: `/question`, `/evaluate`, `/followup` 등 RESTful 엔드포인트 제공

---

## ⚡ 설치 및 실행 방법

### 1. 백엔드

```bash
poetry install
poetry run python rag_agent/app.py
```

### 2. 프론트엔드

```bash
cd frontend
pnpm install
pnpm run dev
```

---

## 💡 사용 예시

1. 자소서/JD 업로드 → 면접 질문 생성
2. 답변 입력 → AI가 평가 및 피드백 제공
3. 꼬리질문/모범답변/다음질문 버튼 클릭 → 대화형 면접 진행

---

## 📄 참고/문서

- [devSpec.md](./devSpec.md) : 상세 개발 명세
- [면접에이전트 기획안 발표.pptx] : 전체 기획안
