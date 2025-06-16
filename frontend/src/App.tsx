import {
  QueryClient,
  QueryClientProvider,
  keepPreviousData,
} from '@tanstack/react-query';
import ChatPage from './page/ChatPage';
import ToastProvider from './shared/toast';
import { useEffect } from 'react';
import { notification } from 'antd';
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      placeholderData: keepPreviousData,
    },
  },
});

function App() {
  const [api, contextHolder] = notification.useNotification();

  useEffect(() => {
    const eventSource = new EventSource('/events'); // 서버 SSE 엔드포인트

    eventSource.onmessage = (event) => {
      api.info({
        message: event.data,
      });
    };

    eventSource.onerror = (err) => {
      console.error('SSE 연결 오류:', err);
      eventSource.close();
    };

    // 컴포넌트 언마운트 시 연결 해제
    return () => {
      eventSource.close();
    };
  }, []);
  return (
    <div className='h-screen w-screen'>
      {contextHolder}
      <QueryClientProvider client={queryClient}>
        <ChatPage />
        <ToastProvider />
      </QueryClientProvider>
    </div>
  );
}

export default App;
