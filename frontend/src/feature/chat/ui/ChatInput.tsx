import { LuSendHorizontal } from 'react-icons/lu';

import { useCallback } from 'react';
import { Button, Form, Input, Tag } from 'antd';
import useChatStore from '../../../shared/chatStore';
import { useQueryClient } from '@tanstack/react-query';
import { useAnswer } from '../hook/useChat';
import { useRef } from 'react';
import { useEffect } from 'react';
import { debounce } from '../../../shared/utils';
// import ActionButtons from '../../../entity/chat/ui/ActionButtons';

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
    <Form
      form={form}
      className='w-full border-2 border-t-0 border-gray-300 rounded-md p-2 flex flex-col h-[17%]'
      onFinish={handleSubmit}>
      <div className='flex flex-row items-center flex-1 w-full'>
        <Form.Item name='message' colon={false} noStyle>
          <style>{`
          textarea:focus {
            border: none;
            outline: none;
            box-shadow: none;
          }ㄱ
          `}</style>
          <Input.TextArea
            ref={textRef}
            placeholder={inputable ? 'Action을 선택해주세요' : '메시지 입력'}
            size='large'
            style={{
              flex: 1,
              resize: 'none',
              marginRight: 10,
              outline: 'none',
              height: '100%',
              width: '100%',
              border: 'none',
            }}
          />
        </Form.Item>
        <div className='flex items-center justify-center border-2 border-gray-300 rounded-full p-2 hover:border-[#4096ff] hover:text-[#4096ff]'>
          <Button
            icon={<LuSendHorizontal size={30} />}
            htmlType='submit'
            style={{
              border: 'none',
            }}
          />
        </div>
      </div>
      <div className='flex flex-row items-center h-[10%] p-6'>
        <Tag
          color='blue'
          className='cursor-pointer'
          onClick={() => form.setFieldsValue({ message: '꼬리질문' })}>
          꼬리질문
        </Tag>
        <Tag
          color='red'
          className='cursor-pointer'
          onClick={() => form.setFieldsValue({ message: '모범답변' })}>
          모범답변
        </Tag>
        <Tag
          color='green'
          className='cursor-pointer'
          onClick={() => form.setFieldsValue({ message: '다음질문' })}>
          다음질문
        </Tag>
      </div>
      {/* <ActionButtons disabled={isPending} /> */}
    </Form>
  );
};

export default ChatInput;
