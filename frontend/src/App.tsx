import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ChatPage from './page/ChatPage';
const queryClient = new QueryClient();

function App() {
  return (
    <>
      <QueryClientProvider client={queryClient}>
        <ChatPage />
      </QueryClientProvider>
    </>
  );
}

export default App;
