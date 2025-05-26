export type ContentType = 'question' | 'answer' | 'modelAnswer';
export type SpeakerType = 'agent' | 'user';
export interface ChatHistoryDTO {
  id: string;
  type: ContentType;
  speaker: SpeakerType;
  content: string;
  isLastMessageAnswer?: boolean;
}
export interface AnswerRequestDTO {
  questionId: string;
  content: string;
}
export interface QuestionDTO {
  id: string;
  content: string;
}
export interface AnswerDTO {
  id: string;
  content: string;
}
