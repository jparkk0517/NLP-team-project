import { create } from 'zustand';

const useFrontStore = create<{
  isLastMessageAnswer: boolean;
  setIsLastMessageAnswer: (isLastMessageAnswer: boolean) => void;
}>((set) => ({
  isLastMessageAnswer: false,
  setIsLastMessageAnswer: (isLastMessageAnswer) => set({ isLastMessageAnswer }),
}));

export default useFrontStore;
