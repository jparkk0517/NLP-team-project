import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { ChatHistoryDTO } from '../../../shared/type';
import Button from '../../../shared/Button';

const UserIcon = () => {
  return (
    <div className='w-[20%]'>
      <span
        className={`text-black rounded-full p-2 w-20 h-20 flex items-center justify-center m-2 bg-green-300`}>
        User
      </span>
    </div>
  );
};

const AgentIcon = () => {
  return (
    <div className='w-[20%]'>
      <span
        className={`text-black rounded-full p-2 w-20 h-20 flex items-center justify-center m-2 bg-yellow-300`}>
        Agent
      </span>
    </div>
  );
};

const Content = ({
  content,
  bottomContent,
}: {
  content: string;
  bottomContent?: React.ReactNode;
}) => {
  return (
    <div>
      <div className='p-2 text-gray-500 rounded-md bg-gray-200 p-2 max-w-[70%] max-h-[300px] min-w-[200px] overflow-scroll'>
        {content}
      </div>
      {bottomContent}
    </div>
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
          <div className='flex p-2'>
            <AgentIcon />
            <Content
              content={content}
              bottomContent={
                type === 'answer' ? (
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
                ) : null
              }
            />
          </div>
        </>
      ) : (
        <>
          <div className='flex flex-row-reverse p-2 items-center'>
            <UserIcon />
            <Content content={content} />
          </div>
        </>
      )}
    </div>
  );
};

export default Message;
