import ChatBody from '../feature/chat/ui/ChatBody';
import ChatHeader from '../feature/chat/ui/ChatHeader';
import ChatInput from '../feature/chat/ui/ChatInput';
import PersonaList from '../feature/persona/ui/PersonaList';
import Panel from '../shared/Panel';
import useChatStore from '../shared/chatStore';
import { useShallow } from 'zustand/react/shallow';
import { usePersona } from '../feature/persona/hook/usePersona';
import { Avatar } from 'antd';

const ChatPage = () => {
  const { data: personaList } = usePersona();
  const { isPending } = useChatStore(
    useShallow((state) => ({
      isPending: state.isPending,
    }))
  );
  return (
    <div className='flex justify-between h-[98%] w-[99%]'>
      <Panel
        title='Agent list'
        minimizeDirection='horizontal'
        className='w-[20%]'
        minimizeContent={personaList?.map((persona, index) => (
          <div key={persona.id} className='mb-4'>
            <Avatar
              src={`https://api.dicebear.com/7.x/miniavs/svg?seed=${index}`}
            />
          </div>
        ))}>
        <PersonaList personaList={personaList ?? []} />
      </Panel>
      <Panel
        title='Chatting'
        minimizeDirection='horizontal'
        isPending={isPending}
        className='w-[100%]'>
        <ChatHeader />
        <ChatBody />
        <ChatInput />
      </Panel>
      {/* <Panel
        title='면접평과결과'
        minimizeDirection='horizontal'
        className='w-[20%]'>
        먖더래ㅑㅈㄷ머래
      </Panel> */}
    </div>
  );
};

export default ChatPage;
