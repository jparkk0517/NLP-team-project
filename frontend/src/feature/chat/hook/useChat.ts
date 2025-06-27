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

const mockData = [] as ChatHistoryDTO[];
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
window.mockData = mockData;
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
    queryFn: async () => {
      return await [...mockData];
    },
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
    // followUpQuestion,
    bestAnswer,
    nextQuestion,
    // isFollowUpQuestionPending,
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
