import { useQuery } from '@tanstack/react-query';
import Message from '../../../entity/chat/ui/Message';
import type { ChatHistoryDTO } from '../../../shared/type';
import { useRef, useEffect } from 'react';
import useFrontStore from '../../../shared/frontStore';

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
  const res = useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => {
      return Promise.resolve(randomMockDataGenerator());
    },
  });
  const { setIsLastMessageAnswer } = useFrontStore();
  useEffect(() => {
    const isLastMessageAnswer =
      res.data?.[res.data.length - 1]?.type === 'answer';
    setIsLastMessageAnswer(isLastMessageAnswer);
  }, [res.data, setIsLastMessageAnswer]);
  return { ...res };
};

const ChatBody = () => {
  const { data } = useChatHistory();
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (chatEndRef.current) {
      setTimeout(() => {
        chatEndRef.current?.scrollIntoView();
      }, 10);
    }
  }, [data]);

  return (
    <div className='flex flex-col justify-center items-center h-[85%] border-b-2 border-gray-300 overflow-scroll'>
      {data?.map((message) => (
        <Message {...message} key={message.id} />
      ))}
      <div ref={chatEndRef} />
    </div>
  );
};

export default ChatBody;
