import ChatBody from '../feature/chat/ui/ChatBody';
import ChatHeader from '../feature/chat/ui/ChatHeader';
import ChatInput from '../feature/chat/ui/ChatInput';
import PersonaList from '../feature/persona/PersonaList';
import Panel from '../shared/Panel';

const ChatPage = () => {
  return (
    <div className='flex   justify-between h-full'>
      <Panel
        title='면접 Agent'
        minimizeDirection='horizontal'
        className='w-[20%]'>
        <PersonaList />
      </Panel>
      <Panel
        title='면접 Agent'
        minimizeDirection='horizontal'
        className='w-[80%] h-full'>
        <ChatHeader />
        <ChatBody />
        <ChatInput />
      </Panel>
    </div>
  );
};

export default ChatPage;
