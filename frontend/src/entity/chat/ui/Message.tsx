import type { ChatHistoryDTO, PersonaDTO } from '../../../shared/type';
import { useRef } from 'react';
import { useEffect } from 'react';

const UserIcon = () => {
  return (
    <div className=''>
      <span
        className={`text-black rounded-full p-2 w-[50px] h-[50px] flex items-center justify-center m-2 bg-green-300`}>
        User
      </span>
    </div>
  );
};

const AgentIcon = ({ persona }: { persona?: PersonaDTO }) => {
  return (
    <div className=''>
      <span
        className={`text-black rounded-full p-2 w-[50px] h-[50px] flex items-center justify-center m-2 bg-yellow-300`}>
        {persona?.name ?? 'Agent'}
      </span>
    </div>
  );
};

const Content = ({
  content,
  textAlign = 'left',
}: {
  content: string;
  textAlign?: 'left' | 'right';
}) => {
  return (
    <div className='flex flex-col justify-end max-w-[80%]'>
      <div
        className={`
          p-2 text-gray-500 rounded-md bg-gray-200 max-w-[70%] overflow-scroll
          ${textAlign === 'right' ? 'flex-row-reverse' : ''}
          scrollbar-hide
        `}>
        {content}
      </div>
    </div>
  );
};

const Message = ({
  speaker,
  content,
  isLastMessage,
  persona,
}: ChatHistoryDTO & {
  isLastMessage: boolean;
}) => {
  const messageRef = useRef<HTMLDivElement>(null);

  const isAgent = speaker === 'agent';

  useEffect(() => {
    if (isLastMessage) {
      setTimeout(() => {
        messageRef.current?.scrollIntoView();
      }, 0);
    }
  }, [isLastMessage]);
  return (
    <div className='w-full items-center my-4' ref={messageRef}>
      {isAgent ? (
        <>
          <div className='flex p-2'>
            <AgentIcon persona={persona} />
            <Content content={content} />
          </div>
        </>
      ) : (
        <>
          <div className='flex flex-row-reverse p-2 items-center'>
            <UserIcon />
            <Content content={content} textAlign='right' />
          </div>
        </>
      )}
    </div>
  );
};

export default Message;
