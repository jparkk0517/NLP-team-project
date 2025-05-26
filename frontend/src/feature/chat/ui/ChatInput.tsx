import { useCallback } from 'react';
import Button from '../../../shared/Button';
import useFrontStore from '../../../shared/frontStore';
import { useQueryClient } from '@tanstack/react-query';
import { useChat } from '../hook/useChat';
import TextArea from '../../../shared/TextArea';
import { useState } from 'react';

const ChatInput = () => {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState('');
  const { mutateAsync: chat, isPending } = useChat();

  const handleSubmit = useCallback(
    async (e?: React.FormEvent<HTMLFormElement>) => {
      e?.preventDefault();
      try {
        await chat(message);
        queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
      } catch (error) {
        console.error(error);
      }
      setMessage('');
    },
    [chat, message, queryClient]
  );
  const { inputable } = useFrontStore();
  return (
    <form className='h-[10%] p-4 flex flex-row' onSubmit={handleSubmit}>
      <TextArea
        placeholder={inputable ? 'Action을 선택해주세요' : '메시지 입력'}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        name='message'
        className='w-[90%] h-full border-2 border-gray-300 rounded-md p-2'
        disabled={!inputable}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            handleSubmit();
          }
        }}
      />
      <Button
        type='submit'
        className={`w-[10%] min-w-[70px]`}
        isLoading={isPending}
        disabled={!inputable || message.length === 0}>
        전송
      </Button>
    </form>
  );
};

export default ChatInput;
