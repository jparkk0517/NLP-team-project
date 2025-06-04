import {
  QueryClient,
  QueryClientProvider,
  keepPreviousData,
} from '@tanstack/react-query';
import ChatPage from './page/ChatPage';
import ToastProvider from './shared/toast';
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      placeholderData: keepPreviousData,
    },
  },
});

function App() {
  return (
    <div className='h-screen w-screen'>
      <QueryClientProvider client={queryClient}>
        <ChatPage />
        <ToastProvider />
      </QueryClientProvider>
    </div>
  );
}

export default App;
