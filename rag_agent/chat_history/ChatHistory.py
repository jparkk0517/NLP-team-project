from typing import Literal, Optional
from uuid import uuid4
from pydantic import BaseModel


ContentType = Literal["question", "answer", "modelAnswer", "evaluate"]
SpeakerType = Literal["agent", "user"]


class ChatItem(BaseModel):
    id: str
    type: ContentType  # "question" | "answer" | "modelAnswer"
    speaker: SpeakerType  # "agent" | "user"
    content: str
    related_chatting_id: Optional[str] = None


class ChatHistory(BaseModel):
    history: list[ChatItem] = []

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
            [
                f"{item.speaker}: {item.content}"
                for item in self.history
                if item.type == "question" or item.type == "answer"
            ]
        )

    # def add_question(self, question: str):
    #     self.question_history.append(
    #         {"question_id": len(self.question_history), "question": question}
    #     )

    #     return self.question_history[-1]["question_id"]

    # def add_answer(self, question_id: str, answer: str):
    #     self.answer_history.append({"question_id": question_id, "answer": answer})

    #     return self.answer_history[-1]["question_id"]
