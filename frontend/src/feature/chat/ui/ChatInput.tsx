import { useCallback } from 'react';
import Button from '../../../shared/Button';
import useFrontStore from '../../../shared/frontStore';
import { useActionState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useChat } from '../hook/useChat';
import TextArea from '../../../shared/TextArea';

type State = {
  message: string;
};
const initialState: State = {
  message: '',
};

const ChatInput = () => {
  const { mutateAsync: chat } = useChat();
  const queryClient = useQueryClient();
  const chatAction = useCallback(
    async (initialState: State, formData: FormData) => {
      try {
        const message = (formData.get('message') as string) ?? '';
        await chat(message);
        queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
      } catch (error) {
        console.error(error);
      }
      return initialState;
    },
    [chat, queryClient]
  );
  const [state, action, isPending] = useActionState(chatAction, initialState);
  const { inputable } = useFrontStore();
  const isDisabled = !inputable || isPending;
  return (
    <form className='h-[10%] p-4 flex flex-row' action={action}>
      <TextArea
        placeholder={isDisabled ? 'Action을 선택해주세요' : '메시지 입력'}
        defaultValue={state.message}
        name='message'
        className='w-[90%] h-full border-2 border-gray-300 rounded-md p-2'
        disabled={isDisabled}
      />
      <Button
        type='submit'
        className={`w-[10%] min-w-[70px]`}
        isLoading={isPending}
        disabled={isDisabled}>
        전송
      </Button>
    </form>
  );
};

export default ChatInput;
