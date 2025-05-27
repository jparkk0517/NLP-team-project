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
    <>
      <QueryClientProvider client={queryClient}>
        <ChatPage />
        <ToastProvider />
      </QueryClientProvider>
    </>
  );
}

export default App;
