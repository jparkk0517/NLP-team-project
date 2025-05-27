import { create } from 'zustand';
import type { ChatHistoryDTO } from './type';

const useChatStore = create<{
  lastMessage?: ChatHistoryDTO;
  lastQuestionId?: string;
  setLastMessage: (lastMessage?: ChatHistoryDTO) => void;
  setLastQuestionId: (lastQuestionId?: string) => void;
}>((set) => ({
  lastMessage: undefined,
  lastQuestionId: undefined,
  setLastMessage: (lastMessage) => set({ lastMessage }),
  setLastQuestionId: (lastQuestionId) => set({ lastQuestionId }),
}));

export default useChatStore;
