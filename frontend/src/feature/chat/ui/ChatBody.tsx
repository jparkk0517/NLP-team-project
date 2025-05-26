import { useQuery } from '@tanstack/react-query';
import Message from '../../../entity/chat/ui/Message';
import type { ChatHistoryDTO } from '../../../shared/type';
import { useRef, useEffect } from 'react';

const randomMockDataGenerator = () => {
  return Array(Math.floor(Math.random() * 100) + 1)
    .fill(0)
    .map((_, index) => {
      const isAgent = Math.random() < 0.5;

      return {
        id: index.toString(),
        type: isAgent ? 'answer' : 'question',
        speaker: isAgent ? 'agent' : 'user',
        content: isAgent
          ? '안녕하세요 면접관입니다.'
          : '안녕하세요 면접자입니다.',
      };
    }) as ChatHistoryDTO[];
};
const useChatHistory = () => {
  return useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => {
      return Promise.resolve(randomMockDataGenerator());
    },
  });
};

const ChatBody = () => {
  const { data, refetch } = useChatHistory();
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (chatEndRef.current) {
      setTimeout(() => {
        chatEndRef.current?.scrollIntoView();
      }, 10);
    }
  }, [data]);

  return (
    <div className='flex-1 flex flex-col justify-center items-center h-[85%] border-b-2 border-gray-300 overflow-scroll p-4'>
      {data?.map((message) => (
        <Message {...message} key={message.id} />
      ))}
      <button
        onClick={() => refetch()}
        className='hover:bg-blue-600 transition-all duration-300 bg-blue-500 text-white px-4 py-2 rounded-md absolute bottom-20 right-10 h-20 w-20 rounded-full'>
        refresh
      </button>
      <div ref={chatEndRef} />
    </div>
  );
};

export default ChatBody;
