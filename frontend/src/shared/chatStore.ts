import { create } from 'zustand';
import type { ChatHistoryDTO, PersonaDTO } from './type';

const useChatStore = create<{
  lastMessage?: ChatHistoryDTO;
  lastQuestionId?: string;
  personaList: PersonaDTO[];
  setLastMessage: (lastMessage?: ChatHistoryDTO) => void;
  setLastQuestionId: (lastQuestionId?: string) => void;
  setPersonaList: (personaList: PersonaDTO[]) => void;
}>((set) => ({
  lastMessage: undefined,
  lastQuestionId: undefined,
  personaList: [],
  setLastMessage: (lastMessage) => set({ lastMessage }),
  setLastQuestionId: (lastQuestionId) => set({ lastQuestionId }),
  setPersonaList: (personaList) => set({ personaList }),
}));

export default useChatStore;
