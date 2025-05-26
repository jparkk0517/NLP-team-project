import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { ChatHistoryDTO, SpeakerType } from '../../../shared/type';
import Button from '../../../shared/Button';

const UserIcon = ({ speaker }: { speaker: SpeakerType }) => {
  return (
    <span
      className={`text-black rounded-full p-2 w-20 h-20 flex items-center justify-center m-2
      ${speaker === 'agent' ? 'bg-yellow-300' : 'bg-green-300'}
      `}>
      {speaker}
    </span>
  );
};

const Content = ({ content }: { content: string }) => {
  return (
    <span className='text-gray-500 rounded-md bg-gray-200 p-2 max-w-[70%]'>
      {content}
    </span>
  );
};

const useRequest = () => {
  const { mutateAsync: followUpQuestion } = useMutation({
    mutationFn: ({ questionId }: { questionId: string }) => {
      console.log(questionId);
      return Promise.resolve(null);
    },
  });

  const { mutateAsync: bestAnswer } = useMutation({
    mutationFn: ({ questionId }: { questionId: string }) => {
      console.log(questionId);
      return Promise.resolve(null);
    },
  });

  const { mutateAsync: nextQuestion } = useMutation({
    mutationFn: () => {
      return Promise.resolve(null);
    },
  });
  return {
    followUpQuestion,
    bestAnswer,
    nextQuestion,
  };
};

const Message = ({ id, type, speaker, content }: ChatHistoryDTO) => {
  const queryClient = useQueryClient();
  const { followUpQuestion, bestAnswer, nextQuestion } = useRequest();
  const isAgent = speaker === 'agent';
  const handleAction = async (
    type: 'followUpQuestion' | 'bestAnswer' | 'nextQuestion'
  ) => {
    try {
      if (type === 'followUpQuestion') {
        await followUpQuestion({ questionId: id });
      } else if (type === 'bestAnswer') {
        await bestAnswer({ questionId: id });
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
    <div className='w-full items-center my-4'>
      {isAgent ? (
        <>
          <div className='flex flex-row items-center p-2'>
            <UserIcon speaker={speaker} />
            <Content content={content} />
          </div>
          {type === 'answer' && (
            <div className='flex flex-row p-2'>
              <Button
                className='mr-2'
                onClick={() => handleAction('followUpQuestion')}>
                꼬리질문
              </Button>
              <Button
                className='mr-2'
                onClick={() => handleAction('bestAnswer')}>
                모범답변
              </Button>
              <Button
                className='mr-2'
                onClick={() => handleAction('nextQuestion')}>
                다음질문
              </Button>
            </div>
          )}
        </>
      ) : (
        <>
          <div className='flex flex-row-reverse w-full items-center'>
            <UserIcon speaker={speaker} />
            <Content content={content} />
          </div>
        </>
      )}
    </div>
  );
};

export default Message;
