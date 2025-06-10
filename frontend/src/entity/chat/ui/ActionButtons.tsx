import { useQueryClient } from '@tanstack/react-query';
import { useRequest } from '../../../feature/chat/hook/useChat';
import Button from '../../../shared/Button';
import useChatStore from '../../../shared/chatStore';
import { useShallow } from 'zustand/shallow';

interface ActionButtonsProps {
  disabled?: boolean;
}

const ActionButtons = ({ disabled = false }: ActionButtonsProps) => {
  const { lastMessage, lastQuestionId } = useChatStore(
    useShallow((state) => ({
      lastMessage: state.lastMessage,
      lastQuestionId: state.lastQuestionId,
    }))
  );

  const queryClient = useQueryClient();
  const { followUpQuestion, bestAnswer, nextQuestion } = useRequest();

  const handleAction = async (
    type: 'followUpQuestion' | 'bestAnswer' | 'nextQuestion'
  ) => {
    try {
      if (!lastQuestionId) return;
      if (type === 'followUpQuestion') {
        await followUpQuestion(lastQuestionId);
      } else if (type === 'bestAnswer') {
        await bestAnswer(lastQuestionId);
      } else if (type === 'nextQuestion') {
        await nextQuestion();
      }
    } catch (error) {
      console.error(error);
    } finally {
      queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
    }
  };
  return (
    <div className='flex flex-row p-2'>
      <Button
        disabled={
          lastMessage?.type === 'question' || disabled || !lastQuestionId
        }
        className='mr-2 '
        onClick={() => handleAction('followUpQuestion')}>
        꼬리질문
      </Button>
      <Button
        disabled={lastMessage?.type !== 'question' || disabled}
        className='mr-2 '
        onClick={() => handleAction('bestAnswer')}>
        모범답변
      </Button>
      <Button
        disabled={disabled}
        className='mr-2 '
        onClick={() => handleAction('nextQuestion')}>
        다음질문
      </Button>
    </div>
  );
};

export default ActionButtons;
