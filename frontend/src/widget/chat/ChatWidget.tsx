import ChatBody from '../../feature/chat/ui/ChatBody';
import ChatHeader from '../../feature/chat/ui/ChatHeader';
import ChatInput from '../../feature/chat/ui/ChatInput';

const ChatWidget = () => {
  return (
    <div className="relative flex h-full flex-col bg-gray-100">
      <ChatHeader />
      <ChatBody />
      <ChatInput />
    </div>
  );
};

export default ChatWidget;
