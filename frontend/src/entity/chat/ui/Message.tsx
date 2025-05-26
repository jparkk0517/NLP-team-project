import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { ChatHistoryDTO, SpeakerType } from '../../../shared/type';

const UserIcon = ({ speaker }: { speaker: SpeakerType }) => {
  return (
    <span className='text-gray-500 rounded-full bg-gray-200 p-2 w-20 h-20 flex items-center justify-center'>
      {speaker}
    </span>
  );
};

const Content = ({ content }: { content: string }) => {
  return (
    <span className='text-gray-500 rounded-md bg-gray-200 p-2'>{content}</span>
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
    if (type === 'followUpQuestion') {
      await followUpQuestion({ questionId: id });
    } else if (type === 'bestAnswer') {
      await bestAnswer({ questionId: id });
    } else if (type === 'nextQuestion') {
      await nextQuestion();
    }
    queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
  };
  return (
    <div className='w-full items-center'>
      {isAgent ? (
        <>
          <div className='flex flex-row items-center'>
            <UserIcon speaker={speaker} />
            <Content content={content} />
          </div>
          {type === 'answer' && (
            <div className='flex flex-row'>
              <button
                className='bg-blue-500 text-white px-4 py-2 rounded-md mr-2'
                onClick={() => handleAction('followUpQuestion')}>
                꼬리질문
              </button>
              <button
                className='bg-blue-500 text-white px-4 py-2 rounded-md mr-2'
                onClick={() => handleAction('bestAnswer')}>
                모범답변
              </button>
              <button
                className='bg-blue-500 text-white px-4 py-2 rounded-md mr-2'
                onClick={() => handleAction('nextQuestion')}>
                다음질문
              </button>
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
