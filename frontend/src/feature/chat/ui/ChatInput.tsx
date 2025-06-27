import { useCallback } from 'react';
import { Form } from 'antd';
import useChatStore from '../../../shared/chatStore';
import { useRef } from 'react';
import { useEffect } from 'react';

const ChatInput = () => {
  const [form] = Form.useForm();
  const textRef = useRef<HTMLTextAreaElement>(null);
  const queryClient = useQueryClient();
  const { answer } = useRequest();
  const  lastMessage  = useChatStore(state => state.lastMessage);
  
  // Form의 values를 감시하여 message 필드의 값을 가져옴
  const messageValue = Form.useWatch('message', form);
  const hasMessage = messageValue && messageValue.trim().length > 0;

  const handleSubmit = useCallback(async () => {
    const message = form.getFieldValue('message');
    const lastMessageId = lastMessage.user?.id;
    if (!lastMessageId || !hasMessage) return;
    try {
      await answer(lastMessageId, message);
    } catch (error) {
      console.error(error);
    } finally {
      queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
      form.resetFields();
    }
  }, [answer, form, lastMessage, queryClient, hasMessage]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  useEffect(() => {
    if (lastMessage.user?.type === 'question') {
      textRef.current?.focus();
    }
  }, [lastMessage.user?.type]);

  return (
    <Form
    style={{margin:'24px'}}
      form={form}
      className="rounded-xl p-1 flex flex-col absolute bottom-0 bg-gray-100 border-2 border-gray-300 left-0 right-0"
      onFinish={handleSubmit}
    >
      <div className="flex flex-col items-center w-full p-2">
        <Form.Item name="message" className="flex-1" colon={false} noStyle>
          <textarea
            ref={textRef}
            // disabled={!inputable}
            placeholder={'메시지를 입력해주세요'}
            onKeyDown={handleKeyDown}
            className="w-full text-black text-shadow-none bg-transparent resize-none focus:ring-0 focus:outline-none focus:border-none mr-2 border-none shadow-none"
          />
        </Form.Item>
        <div className="grid justify-end w-full h-full mt-2">
          <button
          style={{boxShadow: 'none'}}
            type="submit"
            className='bg-white rounded-full p-2 hover:bg-gray-200 cursor-pointer flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-100 shadow-none hover:shadow-none box-shadow-none'
            disabled={ !hasMessage}
          >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="lucide lucide-arrow-up"
      >
        <path d="m5 12 7-7 7 7" />
        <path d="M12 19V5" />
      </svg>
          </button>
        </div>
      </div>
    </Form>
  );
};

export default ChatInput;
