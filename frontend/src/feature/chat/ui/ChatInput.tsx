import { useCallback } from 'react';
import Button from '../../../shared/Button';
import useChatStore from '../../../shared/chatStore';
import { useQueryClient } from '@tanstack/react-query';
import { useAnswer } from '../hook/useChat';
import TextArea from '../../../shared/TextArea';
import { useState } from 'react';
import { useRef } from 'react';
import { useEffect } from 'react';
import { debounce } from '../../../shared/utils';
import ActionButtons from '../../../entity/chat/ui/ActionButtons';

const ChatInput = () => {
  const lastMessage = useChatStore((state) => state.lastMessage);

  const queryClient = useQueryClient();
  const [message, setMessage] = useState('');
  const { mutateAsync: chat, isPending } = useAnswer();

  const inputable = lastMessage?.type === 'question' && !isPending;
  const textRef = useRef<HTMLTextAreaElement>(null);
  const handleSubmit = useCallback(
    async (e?: React.FormEvent<HTMLFormElement>) => {
      e?.preventDefault();
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
      } catch (error) {
        console.error(error);
      } finally {
        queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
        form.resetFields();
      }
    },
    [chat, inputable, lastMessage, message, queryClient]
  );

  useEffect(() => {
    if (inputable) {
      textRef.current?.focus();
    }
  }, [inputable]);
  return (
    <>
      <ActionButtons disabled={isPending} />
      <form className='max-h-[100px] p-4 flex flex-row' onSubmit={handleSubmit}>
        <TextArea
          ref={textRef}
          placeholder={inputable ? 'Action을 선택해주세요' : '메시지 입력'}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          name='message'
          className='w-[90%] h-full border-2 border-gray-300 rounded-md p-2'
          disabled={!inputable}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.shiftKey) {
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
    </>
  );
};

export default ChatInput;
