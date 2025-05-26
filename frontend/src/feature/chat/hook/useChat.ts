import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import useFrontStore from '../../../shared/frontStore';
import type { ChatHistoryDTO } from '../../../shared/type';

const mockData = [] as ChatHistoryDTO[];
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
window.mockData = mockData;
const useChatHistory = () => {
  const res = useQuery({
    queryKey: ['chatHistory'],
    queryFn: async () => {
      return await [...mockData];
    },
  });
  const { setInputable } = useFrontStore();
  useEffect(() => {
    const lastMessage = res.data?.[res.data.length - 1];
    setInputable(
      !!lastMessage &&
        lastMessage.speaker === 'agent' &&
        lastMessage.type === 'question'
    );
  }, [res.data, setInputable]);
  return {
    ...res,
    data: res.data?.map((data, id) => ({
      ...data,
      isLastMessageAnswer:
        data.speaker === 'agent' &&
        ['answer', 'modelAnswer'].includes(data.type) &&
        id === res.data.length - 1,
    })),
  };
};

const useRequest = () => {
  const {
    mutateAsync: followUpQuestion,
    isPending: isFollowUpQuestionPending,
  } = useMutation({
    mutationFn: async ({ questionId }: { questionId: string }) => {
      mockData.push({
        id: mockData.length.toString(),
        type: 'question',
        speaker: 'agent',
        content: `${questionId} 에 대한 꼬리질문`,
      });
      await new Promise((resolve) => setTimeout(resolve, 500));
      return await Promise.resolve(null);
    },
  });

  const { mutateAsync: bestAnswer, isPending: isBestAnswerPending } =
    useMutation({
      mutationFn: async ({ questionId }: { questionId: string }) => {
        mockData.push({
          id: mockData.length.toString(),
          type: 'modelAnswer',
          speaker: 'agent',
          content: `${questionId} 에 대한 최적의 답변`,
        });
        await new Promise((resolve) => setTimeout(resolve, 500));
        return await Promise.resolve(null);
      },
    });

  const { mutateAsync: nextQuestion, isPending: isNextQuestionPending } =
    useMutation({
      mutationFn: async () => {
        mockData.push({
          id: mockData.length.toString(),
          type: 'question',
          speaker: 'agent',
          content: '새로운 질문입니다.',
        });
        await new Promise((resolve) => setTimeout(resolve, 500));
        return await Promise.resolve(null);
      },
    });
  return {
    followUpQuestion,
    bestAnswer,
    nextQuestion,
    isFollowUpQuestionPending,
    isBestAnswerPending,
    isNextQuestionPending,
  };
};

const useChat = () => {
  return useMutation({
    mutationFn: async (message: string) => {
      mockData.push({
        id: mockData.length.toString(),
        type: 'question',
        speaker: 'user',
        content: message,
      });
      mockData.push({
        id: mockData.length.toString(),
        type: 'answer',
        speaker: 'agent',
        content: `${message} 는 훌륭한 답변이에요.`,
      });
      await new Promise((resolve) => setTimeout(resolve, 500));
      return await Promise.resolve(null);
    },
  });
};

export { useChatHistory, useRequest, useChat };
