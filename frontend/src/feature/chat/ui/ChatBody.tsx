import Message from '../../../entity/chat/ui/Message';
import { useRef, useEffect } from 'react';
import { useMemo } from 'react';
import { useChatHistory, useRequest } from '../hook/useChat';
import { memo } from 'react';

const ChatBody = () => {
  const chatBodyRef = useRef<HTMLDivElement | null>(null);
  const isFirst = useRef(true);
  const { nextQuestion } = useRequest();
  const { data, refetch } = useChatHistory();
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const messages = useMemo(() => {
    return data?.map((message) => <Message {...message} key={message.id} />);
  }, [data]);

  useEffect(() => {
    if (data?.length === 0) {
      if (!isFirst.current) return;
      isFirst.current = false;
      nextQuestion().then(() => {
        refetch();
      });
    }

    if (chatEndRef.current) {
      chatEndRef.current?.scrollIntoView();
    }
  }, [data, nextQuestion, refetch]);

  return (
    <div
      className='flex flex-col border-b-2 border-gray-300 overflow-scroll flex-grow'
      style={{ height: 'calc(95% - 100px)' }}
      ref={chatBodyRef}>
      {messages}
      <div ref={chatEndRef} />
    </div>
  );
};

export default memo(ChatBody);
