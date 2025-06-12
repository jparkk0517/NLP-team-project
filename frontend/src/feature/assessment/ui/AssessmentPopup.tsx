import LoadingSpinner from '../../../shared/LoadingSpinner';
import { useAssessment } from '../hook/useAssessment';

const AssessmentPopup = () => {
  const { data, isFetching } = useAssessment();
  return (
    <div className='flex flex-col gap-2 p-4'>
      <h2 className='text-2xl font-bold'>평가 결과</h2>
      {isFetching ? (
        <LoadingSpinner />
      ) : (
        <ul>
          <li>종합 평가: {data?.overallEvaluation}</li>
          <li>논리성: {data?.logicScore}</li>
          <li>직무적합성: {data?.jobFitScore}</li>
          <li>핵심가치 부합성: {data?.coreValueFitScore}</li>
          <li>커뮤니케이션 능력: {data?.communicationScore}</li>
          <li>평균 점수: {data?.averageScore}</li>
        </ul>
      )}
    </div>
  );
};

export default AssessmentPopup;
