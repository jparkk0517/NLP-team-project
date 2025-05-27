import { useEffect } from 'react';
import { create } from 'zustand';
type ToastType = 'success' | 'error';

type Toast = {
  message: string;
  type: ToastType;
  duration?: number;
};
const useToast = create<{
  toast: Toast[];
  setToast: (toast: Toast[]) => void;
}>((set) => ({
  toast: [],
  setToast: (toast: Toast[]) => set({ toast: [...toast] }),
}));

const Toast = ({ message, type, duration = 3000 }: Toast) => {
  useEffect(() => {
    setTimeout(() => {
      useToast.setState({
        toast: useToast.getState().toast.filter((t) => t.message !== message),
      });
    }, duration);
  }, [duration, message]);
  return (
    <div
      className={`
      -translate-x-1/2
      w-fit p-2 rounded-md text-white
      z-50
    ${type === 'success' ? 'bg-green-500' : 'bg-red-500'}`}>
      {message}
    </div>
  );
};

const ToastProvider = () => {
  const { toast } = useToast();
  return (
    <div
      className='
    pointer-events-none
    fixed bottom-0 right-0 w-full h-full flex flex-col-reverse items-center justify-center'>
      {toast.map((t) => (
        <Toast key={t.message} {...t} />
      ))}
    </div>
  );
};

const toastSuccess = (message: string) => {
  useToast.setState({
    toast: [...useToast.getState().toast, { message, type: 'success' }],
  });
};
const toastError = (message: string) => {
  useToast.setState({
    toast: [...useToast.getState().toast, { message, type: 'error' }],
  });
};

export { toastSuccess, toastError };
export default ToastProvider;
