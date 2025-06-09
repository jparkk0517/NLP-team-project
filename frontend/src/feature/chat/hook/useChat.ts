import { useMutation, useQuery } from '@tanstack/react-query';
import { useCallback, useEffect } from 'react';
import useChatStore from '../../../shared/chatStore';
import { Api } from '../../../shared/Api';
import type { ChatHistoryDTO, RequestInputDTO } from '../../../shared/type';
import { useRef } from 'react';
import { useShallow } from 'zustand/shallow';

const useChatHistory = () => {
  const first = useRef(true);
  const { nextQuestion } = useRequest();
  const res = useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => Api.GET<ChatHistoryDTO[]>('/chatHistory'),
  });
  const { setLastMessage, setLastQuestionId } = useChatStore(
    useShallow((state) => ({
      setLastMessage: state.setLastMessage,
      setLastQuestionId: state.setLastQuestionId,
    }))
  );
  useEffect(() => {
    const lastMessage = res.data?.[res.data.length - 1];
    const lastQuestionId = [...(res.data ?? [])]
      .reverse()
      .find((item) => item.type === 'question')?.id;
    setLastMessage(lastMessage);
    setLastQuestionId(lastQuestionId);
  }, [res.data, setLastMessage, setLastQuestionId]);

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
  const { mutateAsync, isPending } = useMutation({
    mutationFn: async (data: RequestInputDTO) => {
      return await Api.POST<RequestInputDTO, ChatHistoryDTO[]>('/', data);
    },
  });

  const followUpQuestion = useCallback(
    async (questionId: string) => {
      try {
        await mutateAsync({
          type: 'followup',
          content: '꼬리질문 해줘',
          related_chatting_id: questionId,
        });
      } catch (e) {
        console.error(e);
      }
    },
    [mutateAsync]
  );

  const bestAnswer = useCallback(
    async (questionId: string) => {
      try {
        await mutateAsync({
          type: 'modelAnswer',
          content: '모범답변 해줘',
          related_chatting_id: questionId,
        });
      } catch (e) {
        console.error(e);
      }
    },
    [mutateAsync]
  );

  const nextQuestion = useCallback(async () => {
    try {
      await mutateAsync({
        type: 'question',
        content: '다음질문 해줘',
      });
    } catch (e) {
      console.error(e);
    }
  }, [mutateAsync]);

  const answer = useCallback(
    async (questionId: string, content: string) => {
      try {
        await mutateAsync({
          type: 'answer',
          content,
          related_chatting_id: questionId,
        });
      } catch (e) {
        console.error(e);
      }
    },
    [mutateAsync]
  );

  const { setIsPending } = useChatStore(
    useShallow((state) => ({
      setIsPending: state.setIsPending,
    }))
  );
  useEffect(() => {
    setIsPending(isPending);
  }, [isPending, setIsPending]);

  return {
    followUpQuestion,
    bestAnswer,
    nextQuestion,
    answer,
  };
};

export { useChatHistory, useRequest };
