import { useMutation, useQuery } from '@tanstack/react-query';
import { useCallback, useEffect } from 'react';
import useChatStore from '../../../shared/chatStore';
import { Api } from '../../../shared/Api';
import type {
  ChatHistoryDTO,
  ContentType,
  RequestInputDTO,
} from '../../../shared/type';

import { useShallow } from 'zustand/shallow';

const useChatHistory = () => {
  const { chatHistory, setChatHistory, setLastMessage } = useChatStore(
    useShallow(state => ({
      chatHistory: state.chatHistory,
      setChatHistory: state.setChatHistory,
      setLastMessage: state.setLastMessage,
    }))
  );
  const res = useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => Api.GET<ChatHistoryDTO[]>('/chatHistory'),
  });

  useEffect(() => {
    setChatHistory(res.data ?? []);
    const reversedData = res.data?.reverse();
    setLastMessage({
      agent: reversedData?.find(item => item.speaker === 'agent') ?? null,
      user: reversedData?.find(item => item.speaker === 'user') ?? null,
    });
  }, [res.data, setChatHistory, setLastMessage]);

  return chatHistory;
};

const useRequest = () => {
  const { setChatHistory, chatHistory } = useChatStore(
    useShallow(state => ({
      setChatHistory: state.setChatHistory,
      chatHistory: state.chatHistory,
    }))
  );
  const { mutateAsync } = useMutation({
    mutationFn: async (data: RequestInputDTO) => {
      setChatHistory([
        ...chatHistory,
        {
          type: data.type as ContentType,
          content: data.content,
          id: '',
          speaker: 'user',
        },
        {
          type: 'answer' as ContentType,
          content: 'isLoading',
          id: '',
          speaker: 'agent',
          isLoading: true,
        },
      ]);
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

  return {
    bestAnswer,
    nextQuestion,
    answer,
    followUpQuestion,
  };
};

export { useChatHistory, useRequest };
