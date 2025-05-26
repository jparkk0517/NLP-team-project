import { create } from 'zustand';

const useFrontStore = create<{
  inputable: boolean;
  setInputable: (inputable: boolean) => void;
}>((set) => ({
  inputable: true,
  setInputable: (inputable) => set({ inputable }),
}));

export default useFrontStore;
