const ChatInput = () => {
  return (
    <div className='h-[10%] p-4 flex flex-row gap-2'>
      <input
        placeholder='메시지 입력'
        type='text'
        className='w-[90%] h-full border-2 border-gray-300 rounded-md p-2'
      />
      <button className='bg-blue-500 text-white px-4 py-2 rounded-md w-[10%]'>
        전송
      </button>
    </div>
  );
};

export default ChatInput;
