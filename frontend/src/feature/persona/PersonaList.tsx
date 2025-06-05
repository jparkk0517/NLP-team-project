import { CiCirclePlus } from 'react-icons/ci';

import { Avatar, Button, Form, Input, List, Modal, Select } from 'antd';
import { useState } from 'react';
import type { PersonaDTO, PersonaType } from '../../shared/type';
import useChatStore from '../../shared/chatStore';

type PersonaForm = Omit<PersonaDTO, 'id'>;
const NewPersonaForm = () => {
  const [form] = Form.useForm<PersonaForm>();
  const handleSubmit = (values: PersonaForm) => {
    console.log(values);
  };

  return (
    <div className='p-4'>
      <Form form={form} onFinish={handleSubmit}>
        <Form.Item
          name='name'
          label='이름'
          rules={[{ required: true, message: '이름을 입력해주세요' }]}
          validateTrigger={['submit']}>
          <Input />
        </Form.Item>
        <Form.Item
          name='type'
          label='타입'
          rules={[{ required: true, message: '타입을 선택해주세요' }]}
          validateTrigger={['submit']}>
          <Select<PersonaType>
            options={[
              { label: '개발자', value: 'developer' },
              { label: '디자이너', value: 'designer' },
              { label: '기획자', value: 'product_manager' },
              { label: '기타', value: 'other' },
            ]}
          />
        </Form.Item>
        <Form.Item label='관심사'>
          <Form.List name='interests'>
            {(fields, { add, remove }) => (
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  rowGap: 0,
                  width: '100%',
                }}>
                {fields.map((field) => (
                  <div className='flex items-unset justify-between w-full'>
                    <Form.Item
                      key={field.key}
                      name={field.name}
                      style={{ width: '90%' }}>
                      <Input />
                    </Form.Item>
                    <Button
                      danger
                      onClick={() => {
                        remove(field.name);
                      }}>
                      제거
                    </Button>
                  </div>
                ))}
                <Button onClick={() => add('')}>+관심사 추가</Button>
              </div>
            )}
          </Form.List>
        </Form.Item>
        <Form.Item name='communicationStyle' label='대화 스타일'>
          <Input.TextArea />
        </Form.Item>
        <Button type='primary' htmlType='submit' className='w-full'>
          면접관 생성
        </Button>
      </Form>
    </div>
  );
};

const PersonaList = () => {
  const personaList = useChatStore((state) => state.personaList);
  const [newPersonaOpen, setNewPersonaOpen] = useState(false);

  return (
    <div className='h-full'>
      <List className='' itemLayout='horizontal'>
        {personaList.map((persona, index) => (
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
        <NewPersonaForm />
      </Modal>
    </div>
  );
};

export default PersonaList;
