import Message from '../../../entity/chat/ui/Message';
import { useRef, useEffect } from 'react';
import { useMemo } from 'react';
import { useChatHistory, useRequest } from '../hook/useChat';
import { debounce } from '../../../shared/utils';
import { useCallback } from 'react';

const ChatBody = () => {
  const isFirst = useRef(true);
  const { nextQuestion } = useRequest();
  const { data, isFetching, refetch } = useChatHistory();
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const messages = useMemo(() => {
    return data?.map((message) => <Message {...message} key={message.id} />);
  }, [data]);

  const firstQuestionDebounce = useCallback(
    debounce(() => {
      if (!isFirst.current) return;
      isFirst.current = false;
      nextQuestion().then(() => {
        refetch();
      });
    }, 10),
    [nextQuestion, refetch]
  );
  useEffect(() => {
    if (data?.length === 0 && !isFetching) {
      return firstQuestionDebounce();
    }

    if (chatEndRef.current) {
      setTimeout(() => {
        chatEndRef.current?.scrollIntoView();
      }, 0);
    }
  }, [data, firstQuestionDebounce, isFetching]);
  return (
    <div className='flex flex-col h-[80%] border-b-2 border-gray-300 overflow-scroll'>
      {messages}
      <div ref={chatEndRef} />
    </div>
  );
};

export default ChatBody;
