import { LuSendHorizontal } from 'react-icons/lu';

import { useCallback } from 'react';
import { Button, Form, Input } from 'antd';
import useChatStore from '../../../shared/chatStore';
import { useQueryClient } from '@tanstack/react-query';
import { useAnswer } from '../hook/useChat';
import { useRef } from 'react';
import { useEffect } from 'react';
import { debounce } from '../../../shared/utils';
import ActionButtons from '../../../entity/chat/ui/ActionButtons';

const ChatInput = () => {
  const [form] = Form.useForm();
  const lastMessage = useChatStore((state) => state.lastMessage);

  const queryClient = useQueryClient();
  const { mutateAsync: chat, isPending } = useAnswer();

  const inputable = lastMessage?.type === 'question' && !isPending;
  const textRef = useRef<HTMLTextAreaElement>(null);
  const handleSubmit = useCallback(async () => {
    const message = form.getFieldValue('message');
    const debounced = debounce(async () => {
      if (!inputable || !lastMessage) return;
      try {
        await chat({
          questionId: lastMessage.id,
          content: message,
        });
        queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
      } catch (error) {
        console.error(error);
      }
    }, 100);
    debounced();
  }, [chat, form, inputable, lastMessage, queryClient]);

  useEffect(() => {
    if (inputable) {
      textRef.current?.focus();
    }
  }, [inputable]);
  return (
    <>
      <ActionButtons disabled={isPending} />
      <Form
        form={form}
        className='max-h-[100px] p-4 flex flex-row'
        onFinish={handleSubmit}>
        <div className='w-full border-2 border-gray-300 rounded-md p-2 flex items-center'>
          <Input.TextArea
            ref={textRef}
            placeholder={inputable ? 'Action을 선택해주세요' : '메시지 입력'}
            name='message'
            size='large'
            style={{
              border: 'none',
              width: '90%',
              resize: 'none',
              marginRight: 10,
              outline: 'none',
            }}
          />
          <Button
            style={{
              height: 50,
              width: 50,
              borderRadius: 50,
            }}
            icon={<LuSendHorizontal size={24} />}
            htmlType='submit'
          />
        </div>
      </Form>
    </>
  );
};

export default ChatInput;
