import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import useChatStore from '../../../shared/chatStore';
import { Api } from '../../../shared/Api';
import type { ChatHistoryDTO } from '../../../shared/type';
import { useRef } from 'react';

const useChatHistory = () => {
  const first = useRef(true);
  const { nextQuestion } = useRequest();
  const res = useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => Api.GET<ChatHistoryDTO[]>('/chatHistory'),
  });
  const { setLastMessage } = useChatStore();
  useEffect(() => {
    const lastMessage = res.data?.[res.data.length - 1];
    setLastMessage(lastMessage);
  }, [res.data, setLastMessage]);

  useEffect(() => {
    if (first.current && res.data?.length === 0) {
      first.current = false;
      nextQuestion().then(() => {
        res.refetch();
      });
    }
  }, [nextQuestion, res, res.data?.length]);

  return res;
};

const useRequest = () => {
  const {
    mutateAsync: followUpQuestion,
    isPending: isFollowUpQuestionPending,
  } = useMutation({
    mutationFn: async ({ questionId }: { questionId: string }) => {
      return await Api.GET<null>('/followUp', {
        questionId,
      });
    },
  });

  const { mutateAsync: bestAnswer, isPending: isBestAnswerPending } =
    useMutation({
      mutationFn: async ({ questionId }: { questionId: string }) =>
        Api.GET<null>('/modelAnswer', {
          questionId,
        }),
    });

  const { mutateAsync: nextQuestion, isPending: isNextQuestionPending } =
    useMutation({
      mutationFn: async () => Api.GET<null>('/question'),
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

const useAnswer = () => {
  return useMutation({
    mutationFn: ({
      questionId,
      content,
    }: {
      questionId: string;
      content: string;
    }) =>
      Api.POST<{ questionId: string; content: string }, null>('/answer', {
        questionId,
        content,
      }),
  });
};

export { useChatHistory, useRequest, useAnswer };
