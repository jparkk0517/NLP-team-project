import Message from '../../../entity/chat/ui/Message';
import { useRef, useCallback, useState, useEffect } from 'react';
import { useMemo } from 'react';
import { memo } from 'react';
import useChatStore from '../../../shared/chatStore';

const useScroll = () => {
  const chatContainerRef = useRef<HTMLDivElement | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const [showScrollDownButton, setShowScrollDownButton] = useState(false);
  const scrollToBottom = useCallback((behavior: ScrollBehavior = 'smooth') => {
    chatEndRef.current?.scrollIntoView({ behavior });
  }, []);

  const handleScroll = useCallback(() => {
    const container = chatContainerRef.current;
    if (container) {
      const { scrollTop, scrollHeight, clientHeight } = container;
      if (scrollHeight - scrollTop > clientHeight + 100) {
        setShowScrollDownButton(true);
      } else {
        setShowScrollDownButton(false);
      }
    }
  }, []);

  const scrolllBottom = useMemo(() => {
    if(!showScrollDownButton) return null;
    return (
      <button
      onClick={() => scrollToBottom()}
      className="absolute z-10 left-1/2 -translate-x-1/2 bottom-[25%] p-2 rounded-full bg-white/70 backdrop-blur-sm shadow-md hover:bg-white transition-all cursor-pointer"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="lucide lucide-arrow-down"
      >
        <path d="M12 5v14" />
        <path d="m19 12-7 7-7-7" />
      </svg>
    </button>)
  }, [scrollToBottom, showScrollDownButton]);
  return {
    chatContainerRef,
    chatEndRef,
    handleScroll,
    scrollToBottom,
    scrolllBottom,
  }
}

const ChatBody = () => {
  const chatHistory  = useChatStore(state => state.chatHistory);
  const { chatContainerRef, chatEndRef, scrolllBottom, handleScroll, scrollToBottom } = useScroll();

  const messages = useMemo(() => {
    return chatHistory?.map((message, idx) => (
      <Message
        {...message}
        key={message.id}
        isLastMessage={idx === chatHistory.length - 1}
      />
    ));
  }, [chatHistory]);


  useEffect(() => {
    const isAtBottom = () => {
      if (!chatContainerRef.current) return true;
      const { scrollHeight, scrollTop, clientHeight } = chatContainerRef.current;
      return scrollHeight - scrollTop <= clientHeight + 200;
    };

    if (isAtBottom()) {
      scrollToBottom('auto');
    }
  }, [chatContainerRef, scrollToBottom]);

  useEffect(() => {
    scrollToBottom('auto');
  }, [chatHistory, scrollToBottom])



  return (
    <div className="relative flex-grow">
      <div
        ref={chatContainerRef}
        onScroll={handleScroll}
        className="absolute inset-0 flex flex-col mb-[20%] overflow-scroll scrollbar-hide hover:scrollbar bg-transparent"
      >
        {messages}
        <div ref={chatEndRef} />
      </div>
      {scrolllBottom}
    </div>
  );
};

export default memo(ChatBody);
