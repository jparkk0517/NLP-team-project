import { useQuery } from '@tanstack/react-query';
import { Api } from '../../../shared/Api';
import type { AssessmentResultDTO } from '../../../shared/type';

const useAssessment = () => {
  return useQuery({
    queryKey: ['assessment'],
    queryFn: () => {
      return Api.GET<AssessmentResultDTO>('/assessment');
    },
  });
};

export { useAssessment };
