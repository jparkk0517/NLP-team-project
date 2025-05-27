import { create } from 'zustand';
import type { ChatHistoryDTO } from './type';

const useChatStore = create<{
  lastMessage?: ChatHistoryDTO;
  setLastMessage: (lastMessage?: ChatHistoryDTO) => void;
}>((set) => ({
  lastMessage: undefined,
  setLastMessage: (lastMessage) => set({ lastMessage }),
}));

export default useChatStore;
