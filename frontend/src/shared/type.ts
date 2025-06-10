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
export type RequestType =
  | 'question'
  | 'followup'
  | 'modelAnswer'
  | 'answer'
  | 'other';
export interface RequestInputDTO {
  type?: RequestType;
  content: string;
  related_chatting_id?: string;
}
export interface PersonaInputDTO {
  type: PersonaType;
  name: string;
  interests?: string[];
  communication_style?: string;
}

export interface PersonaDTO {
  id: string;
  type: PersonaType;
  name: string;
  interests?: string[];
  communication_style?: string;
}
