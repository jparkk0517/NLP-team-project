# LangChain 기반 면접관 모드 RAG 시스템 개발 구조 설명서

## 1. 시스템 개요
본 시스템은 사용자가 입력한 자소서, JD, 기업 정보를 기반으로  
1) 면접 질문을 생성하고  
2) 답변을 평가하며  
3) 꼬리질문, 모범답변, 다음 질문을 제시하는  
AI 면접 시뮬레이터이다.  

LangChain을 기반으로 Retrieval-Augmented Generation (RAG) 구조를 활용하며,  
사용자 인터랙션은 채팅 기반 UI로 구현한다.

---

## 2. 주요 구성 요소

### ① 문서 저장소 (Vector DB)
- 저장 대상: 자소서, JD, 기업정보 등
- 분할 방식: RecursiveCharacterTextSplitter (chunk_size=500, overlap=50)
- 임베딩 모델: OpenAIEmbeddings 또는 HuggingFace
- 벡터 저장소: ChromaDB (persist_directory 구조 유지)

### ② 체인 구성 (LangChain 기반)
- 질문 생성 체인: RetrievalQA.from_chain_type + PromptTemplate
- 평가 체인: LLMChain + custom prompt (답변 평가)
- 꼬리질문/모범답변 체인: FollowUpPrompt + LLMChain

### ③ API 서버 (FastAPI)
- API Endpoint:
  - `/question`: 면접 질문 생성
  - `/evaluate`: 사용자 답변 평가
  - `/followup`: 꼬리질문 / 모범답변 / 다음질문 응답
- 입력값 예시:
  - `/evaluate` : `{ "user_answer": "..." }`
  - `/followup`: `{ "user_answer": "...", "mode": "tail|model|next" }`

### ④ 프론트엔드 연동 흐름
- 질문 출력 → 사용자 답변 입력 → 평가 결과 출력 + 버튼 제시
- 버튼 클릭 시 `/followup` 호출하여 새로운 질문 흐름

---

## 3. 프롬프트 설계 (요약)

### [질문 생성 Prompt]
당신은 면접관입니다. 다음 자소서와 JD를 기반으로  
사용자에게 직무 관련 면접 질문을 하십시오.  
(자소서 및 JD는 context로 제공)

### [답변 평가 Prompt]
사용자 답변을 기준으로 다음 항목을 평가하세요:  
1) 논리성, 2) 구체성, 3) 직무적합성  
또한 개선 제안을 하나 작성하십시오.

### [Followup Prompt]
사용자 답변에 기반하여 다음 중 하나를 수행하십시오:  
- 꼬리질문 생성  
- 모범답변 예시 작성  
- 다음 질문 생성  
입력값 mode에 따라 동작이 달라집니다.

---

## 4. 주요 파일 및 역할

```
📁 rag_agent/
│
├── app.py                      # FastAPI 서버 진입점
├── chains/
│   ├── interview_chain.py      # 질문 생성 체인
│   ├── evaluate_chain.py       # 평가 체인
│   └── followup_chain.py       # 꼬리질문/모범답변 체인
├── data/
│   └── resume_jd_docs/         # 문서 저장 경로
└── vectorstore/
    └── chroma_db/              # 임베딩된 벡터 저장소
```

---

## 5. 요청 시 유의사항
- 프롬프트에 문서 context가 항상 포함되어야 함
- 평가 결과는 “항목별 점수 + 개선 제안” 형식으로 출력
- followup은 반드시 버튼 클릭에 따라 세 가지 중 하나를 선택
- 프론트에서 받은 히스토리를 context로 넘길 수 있음

---

## 6. 확장 고려사항 (선택)
- 음성 답변(STT) → 텍스트 변환 → 평가 흐름 추가
- GPT 외 LLM으로 전환 시 embedding/chain 재정의
- 사용자 인터뷰 이력 저장 및 요약 기능

---

## 7. 개발 목표 문장 예시 (ChatGPT에 전달할 prompt 예시)
"아래 DevSpec.txt를 참고해서 rag_agent 디렉토리 구조를 만들고,  
FastAPI와 LangChain으로 각 체인을 구현해줘.  
또한 프롬프트 내용은 위에서 명시한 것들을 기준으로 생성해줘."