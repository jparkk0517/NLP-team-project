import { CiCirclePlus } from 'react-icons/ci';

import { Avatar, Button, List, Modal } from 'antd';
import { useCallback, useState } from 'react';
import NewPersonaForm from '../../../entity/persona/ui/NewPersonaForm';
import { usePersonaMutation, usePersona } from '../hook/usePersona';
import type { PersonaInputDTO } from '../../../shared/type';

const PersonaList = () => {
  const [newPersonaOpen, setNewPersonaOpen] = useState(false);
  const { addPersona, deletePersona } = usePersonaMutation();
  const { data: personaList } = usePersona();

  const handleAddPersona = useCallback(
    async (persona: PersonaInputDTO) => {
      addPersona(persona);
      setNewPersonaOpen(false);
    },
    [addPersona]
  );

  const handleDeletePersona = useCallback(
    async (personaId: string) => {
      deletePersona(personaId);
    },
    [deletePersona]
  );

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
              title={`${persona.name} (${persona.type})`}
              description={persona.interests?.join(', ')}
            />
            <Button
              key='delete'
              type='text'
              danger
              onClick={() => handleDeletePersona(persona.id)}>
              나가기
            </Button>
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
        <NewPersonaForm addPersona={handleAddPersona} />
      </Modal>
    </div>
  );
};

export default PersonaList;
