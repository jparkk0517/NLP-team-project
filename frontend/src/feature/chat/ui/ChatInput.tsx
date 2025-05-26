import Button from '../../../shared/Button';
import useFrontStore from '../../../shared/frontStore';

const ChatInput = () => {
  const { isLastMessageAnswer } = useFrontStore();
  return (
    <div className='h-[10%] p-4 flex flex-row'>
      <input
        placeholder={
          isLastMessageAnswer ? 'Action을 선택해주세요' : '메시지 입력'
        }
        type='text'
        className='w-[90%] h-full border-2 border-gray-300 rounded-md p-2'
        disabled={isLastMessageAnswer}
      />
      <Button
        className={`w-[10%] min-w-[70px] ${
          isLastMessageAnswer ? 'opacity-50' : ''
        }`}
        disabled={isLastMessageAnswer}>
        전송
      </Button>
    </div>
  );
};

export default ChatInput;
