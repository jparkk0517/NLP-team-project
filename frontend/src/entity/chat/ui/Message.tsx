import type { ChatHistoryDTO, PersonaDTO } from '../../../shared/type';
import { useRef } from 'react';

const UserIcon = () => {
  return (
    <div className="">
      <span
        className={`text-black rounded-full p-2 w-[50px] h-[50px] flex items-center justify-center m-2 bg-green-300`}
      >
        User
      </span>
    </div>
  );
};

const AgentIcon = () => {
  return (
    <div className="">
      <span
        className={`text-black rounded-full p-2 w-[50px] h-[50px] flex items-center justify-center m-2 bg-yellow-300`}
      >
        {persona?.name ?? 'Agent'}
      </span>
    </div>
  );
};

const Content = ({
  content,
  bottomContent,
  textAlign = 'left',
}: {
  content: string;
  textAlign?: 'left' | 'right';
  bottomContent?: React.ReactNode;
}) => {
  return (
    <div className={`flex flex-col justify-end max-w-[80%]
          p-2 text-gray-500 rounded-md bg-gray-200 overflow-scroll
          ${textAlign === 'right' ? 'flex-row-reverse' : ''}
          scrollbar-hide
          whitespace-pre-line
          break-words`}
      >
      <div
        className={`
        ${textAlign === 'right' ? 'text-right' : 'text-left'}
        `}
      >
        {content}
      </div>
      {bottomContent}
    </div>
  );
};

const LoadingContent = () => {
  return (
    <div className="flex flex-col justify-end max-w-[80%] p-2 text-gray-500 rounded-md bg-gray-200">
      <div className="flex items-center space-x-1">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
        <span className="text-sm text-gray-400 ml-2">응답을 생성하고 있습니다...</span>
      </div>
    </div>
  );
}

const Message = ({
  id,
  speaker,
  content,
  // isLastMessage,
  isLoading,
  persona,
}: ChatHistoryDTO & {
  isLastMessage: boolean;
}) => {
  const messageRef = useRef<HTMLDivElement>(null);

  const isAgent = speaker === 'agent';

  return (
    <div className="w-full items-center my-4" ref={messageRef}>
      { 
      isAgent ? (
        <>
          <div className="flex p-2">
            <AgentIcon persona={persona} />
            {isLoading ? <LoadingContent /> : <Content content={content} />}
          </div>
        </>
      ) : (
        <>
          <div className="flex flex-row-reverse p-2 items-center">
            <UserIcon />
            <Content content={content} textAlign="right" />
          </div>
        </>
      )}
    </div>
  );
};

export default Message;
