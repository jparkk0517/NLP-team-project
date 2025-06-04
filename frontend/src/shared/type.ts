export type ContentType = 'question' | 'answer' | 'modelAnswer' | 'evaluate';
export type SpeakerType = 'agent' | 'user';
export type PersonaType =
  | 'developer'
  | 'designer'
  | 'product_manager'
  | 'other';
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

export interface AssessmentResultDTO {
  logicScore: number;
  jobFitScore: number;
  coreValueFitScore: number;
  communicationScore: number;
  averageScore: number;
}

export interface PersonaDTO {
  id: string;
  name: string;
  type: PersonaType;
  interests?: string[];
  communicationStyle?: string;
}
