import PersonaList from '../feature/persona/ui/PersonaList';
import Panel from '../shared/Panel';
import { usePersona } from '../feature/persona/hook/usePersona';
import { Avatar } from 'antd';
import ChatWidget from '../widget/chat/ChatWidget';
import { useChatHistory } from '../feature/chat/hook/useChat';

const ChatPage = () => {
  const { data: personaList } = usePersona();
  useChatHistory()
  return (
    <div className="flex justify-between h-[98%] w-[99%]">
      <Panel
        title="Agent list"
        minimizeDirection="horizontal"
        className="w-[20%]"
        minimizeContent={personaList?.map((persona, index) => (
          <div key={persona.id} className="mb-4">
            <Avatar
              src={`https://api.dicebear.com/7.x/miniavs/svg?seed=${index}`}
            />
          </div>
        ))}
      >
        <PersonaList personaList={personaList ?? []} />
      </Panel>
      <Panel
        title="Chatting"
        minimizeDirection="horizontal"
        className="w-[100%]"
      >
        <ChatWidget />
      </Panel>
    </div>
  );
};

export default ChatPage;
