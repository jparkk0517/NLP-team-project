from langchain.prompts import PromptTemplate
from typing import Literal, Optional, Self
from uuid import uuid4
from pydantic import BaseModel, Field
from datetime import datetime
from ..chat_history.Singleton import Singleton


ContentType = Literal[
    "question", "answer", "modelAnswer", "evaluate", "rerankedModelAnswer"
]
SpeakerType = Literal["agent", "user"]


class ChatItem(BaseModel):
    id: str
    type: ContentType  # "question" | "answer" | "modelAnswer"
    speaker: SpeakerType  # "agent" | "user"
    content: str
    related_chatting_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class ChatHistory(Singleton):
    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.history = []

    def add(
        self,
        type: ContentType,
        speaker: SpeakerType,
        content: str,
        related_chatting_id: Optional[str] = None,
    ) -> str:
        id = str(uuid4().hex[:8])
        self.history.append(
            ChatItem(
                id=id,
                type=type,
                speaker=speaker,
                content=content,
                related_chatting_id=related_chatting_id,
            )
        )
        return id

    def get_all_history(self) -> list[ChatItem]:
        return self.history

    def get_latest_question_id(self) -> Optional[str]:
        for item in reversed(self.history):
            if item.type == "question":
                return item.id
        return None

    def get_chat_history_every_related_by_chatting_id(
        self, related_chatting_id: str
    ) -> list[ChatItem]:
        result = []
        current_id = related_chatting_id
        while current_id is not None:
            item = self.get_question_by_id(current_id)
            if item is None:
                break
            result.append(item)
            current_id = item.related_chatting_id
        return result

    def get_question_by_id(self, question_id: str) -> Optional[ChatItem]:
        for item in self.history:
            if item.id == question_id and item.type == "question":
                return item
        return None

    def get_answer_by_question_id(self, question_id: str) -> Optional[ChatItem]:
        for item in self.history:
            if item.related_chatting_id == question_id and item.type == "answer":
                return item
        return None

    def validate_question_exists(self, question_id: str) -> bool:
        return any(
            item.id == question_id and item.type == "question" for item in self.history
        )

    def get_all_history_as_string(self) -> str:
        return "\n".join(
            [f"{item.speaker}({item.id}): {item.content}" for item in self.history]
        )

    def get_chat_history_context_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            template=f"""
            [상황]
            당신은 지원자의 이력서와 직무 설명서를 보고 지원자를 평가하고 있습니다.
            현재까지 면접의 대화 내용은 다음과 같습니다.
            {self.get_all_history_as_string()}
            """,
        )
