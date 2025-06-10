import { create } from 'zustand';
import type { ChatHistoryDTO } from './type';

const useChatStore = create<{
  lastMessage?: ChatHistoryDTO;
  lastQuestionId?: string;
  isPending: boolean;
  setLastMessage: (lastMessage?: ChatHistoryDTO) => void;
  setLastQuestionId: (lastQuestionId?: string) => void;
  setIsPending: (isPending: boolean) => void;
}>((set) => ({
  lastMessage: undefined,
  lastQuestionId: undefined,
  isPending: true,
  setLastMessage: (lastMessage) => set({ lastMessage }),
  setLastQuestionId: (lastQuestionId) => set({ lastQuestionId }),
  setIsPending: (isPending) => set({ isPending }),
}));

export default useChatStore;
