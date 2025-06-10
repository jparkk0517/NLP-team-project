import { LuSendHorizontal } from 'react-icons/lu';

import { useCallback } from 'react';
import { Button, Form, Input, Tag } from 'antd';
import useChatStore from '../../../shared/chatStore';
import { useRef } from 'react';
import { useEffect } from 'react';
import { debounce } from '../../../shared/utils';
import { useRequest } from '../hook/useChat';
import { useQueryClient } from '@tanstack/react-query';

const ChatInput = () => {
  const [form] = Form.useForm();
  const lastMessage = useChatStore((state) => state.lastMessage);
  const textRef = useRef<HTMLTextAreaElement>(null);
  const queryClient = useQueryClient();
  const { answer, bestAnswer, followUpQuestion, nextQuestion } = useRequest();

  const inputable = lastMessage?.type === 'question';

  const handleSubmit = useCallback(async () => {
    const message = form.getFieldValue('message');
    const debounced = debounce(async () => {
      if (!inputable || !lastMessage) return;
      try {
        await answer(lastMessage.id, message);
      } catch (error) {
        console.error(error);
      }
    }, 100);
    debounced();
  }, [answer, form, inputable, lastMessage]);

  const handleStaticAction = useCallback(
    async (action: 'followUpQuestion' | 'bestAnswer' | 'nextQuestion') => {
      if (!inputable || !lastMessage) return;
      try {
        if (action === 'followUpQuestion') {
          form.setFieldsValue({ message: '꼬리질문 해줘' });
          await followUpQuestion(lastMessage.id);
        } else if (action === 'bestAnswer') {
          form.setFieldsValue({ message: '모범답변 만들어줘' });
          await bestAnswer(lastMessage.id);
        } else if (action === 'nextQuestion') {
          form.setFieldsValue({ message: '다음질문 해줘' });
          await nextQuestion();
        }
      } catch (error) {
        console.error(error);
      } finally {
        queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
        form.resetFields();
      }
    },
    [
      bestAnswer,
      followUpQuestion,
      form,
      inputable,
      lastMessage,
      nextQuestion,
      queryClient,
    ]
  );

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
          onClick={() => handleStaticAction('followUpQuestion')}>
          꼬리질문
        </Tag>
        <Tag
          color='red'
          className='cursor-pointer'
          onClick={() => handleStaticAction('bestAnswer')}>
          모범답변
        </Tag>
        <Tag
          color='green'
          className='cursor-pointer'
          onClick={() => handleStaticAction('nextQuestion')}>
          다음질문
        </Tag>
      </div>
      {/* <ActionButtons disabled={isPending} /> */}
    </Form>
  );
};

export default ChatInput;
