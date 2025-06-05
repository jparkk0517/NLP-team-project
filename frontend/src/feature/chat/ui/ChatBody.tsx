import Message from '../../../entity/chat/ui/Message';
import { useRef } from 'react';
import { useMemo } from 'react';
import { useChatHistory } from '../hook/useChat';
import { memo } from 'react';

const ChatBody = () => {
  const { data } = useChatHistory();
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const messages = useMemo(() => {
    return data?.map((message, idx) => (
      <Message
        {...message}
        key={message.id}
        isLastMessage={idx === data.length - 1}
      />
    ));
  }, [data]);

  return (
    <div
      className='flex flex-col border-b-2 border-gray-300 overflow-scroll scrollbar-hide hover:scrollbar flex-grow'
      style={{ height: '83%' }}>
      {messages}
      <div ref={chatEndRef} />
    </div>
  );
};

export default memo(ChatBody);
