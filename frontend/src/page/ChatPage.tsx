import ChatBody from '../feature/chat/ui/ChatBody';
import ChatHeader from '../feature/chat/ui/ChatHeader';
import ChatInput from '../feature/chat/ui/ChatInput';

const ChatPage = () => {
  return (
    <div className='flex flex-col h-screen w-screen min-w-[450px] min-h-[600px] overflow-scroll'>
      <ChatHeader />
      <ChatBody />
      <ChatInput />
    </div>
  );
};

export default ChatPage;
