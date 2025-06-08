import { CiCirclePlus } from 'react-icons/ci';

import { Avatar, List, Modal } from 'antd';
import { useState } from 'react';
import NewPersonaForm from '../../../entity/persona/ui/NewPersonaForm';
import { usePersonaMutation, usePersona } from '../hook/usePersona';

const PersonaList = () => {
  const [newPersonaOpen, setNewPersonaOpen] = useState(false);
  const { addPersona, deletePersona } = usePersonaMutation();
  const { data: personaList } = usePersona();
  return (
    <div className='h-full'>
      <List className='' itemLayout='horizontal'>
        {personaList?.map((persona, index) => (
          <List.Item>
            <List.Item.Meta
              avatar={
                <Avatar
                  src={`https://api.dicebear.com/7.x/miniavs/svg?seed=${index}`}
                  style={{ backgroundColor: 'red' }}
                />
              }
              title={persona.name}
            />
          </List.Item>
        ))}

        <List.Item
          className='cursor-pointer'
          onClick={() => setNewPersonaOpen(true)}>
          <List.Item.Meta
            avatar={<CiCirclePlus size={24} />}
            title={'면접관 추가하기'}
          />
        </List.Item>
      </List>
      <Modal
        open={newPersonaOpen}
        onCancel={() => setNewPersonaOpen(false)}
        footer={null}
        destroyOnHidden>
        <NewPersonaForm addPersona={addPersona} deletePersona={deletePersona} />
      </Modal>
    </div>
  );
};

export default PersonaList;
