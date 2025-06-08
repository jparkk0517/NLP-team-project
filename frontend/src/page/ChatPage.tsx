import ChatBody from '../feature/chat/ui/ChatBody';
import ChatHeader from '../feature/chat/ui/ChatHeader';
import ChatInput from '../feature/chat/ui/ChatInput';
import PersonaList from '../feature/persona/ui/PersonaList';
import Panel from '../shared/Panel';

const ChatPage = () => {
  return (
    <div className='flex justify-between h-[98%] w-[99%]'>
      <Panel
        title='Agent list'
        minimizeDirection='horizontal'
        className='w-[20%]'>
        <PersonaList />
      </Panel>
      <Panel
        title='Chatting'
        minimizeDirection='horizontal'
        className='w-[80%]'>
        <ChatHeader />
        <ChatBody />
        <ChatInput />
      </Panel>
    </div>
  );
};

export default ChatPage;
