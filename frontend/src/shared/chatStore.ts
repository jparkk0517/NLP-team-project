import { create } from 'zustand';
import type { ChatHistoryDTO } from './type';

const useChatStore = create<{
  chatHistory: ChatHistoryDTO[];
  setChatHistory: (chatHistory: ChatHistoryDTO[]) => void;
  lastMessage: {
    agent: ChatHistoryDTO | null;
    user: ChatHistoryDTO | null;
  };
  setLastMessage: (lastMessage: {
    agent: ChatHistoryDTO | null;
    user: ChatHistoryDTO | null;
  }) => void;
}>(set => ({
  chatHistory: [],
  setChatHistory: chatHistory => set({ chatHistory }),
  lastMessage: {
    agent: null,
    user: null,
  },
  setLastMessage: lastMessage => set({ lastMessage }),
}));

export default useChatStore;
