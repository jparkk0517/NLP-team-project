const ChatHeader = () => {
  return (
<<<<<<< Updated upstream
    <div className='flex items-center justify-around h-16 p-4 h-[5%] border-b-2 border-gray-300'>
      <div className='flex items-center gap-2'>
        <span>Chat</span>
      </div>
=======
    <div className="relative flex items-center justify-around p-4 h-[5%] border-b-2 border-gray-300">
      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-2xl cursor-pointer">
        <div className="flex items-center gap-2" onClick={handleAssessment}>
          <MdOutlineAssessment className="text-1xl" />
          <span className="text-sm">평가</span>
        </div>
      </div>
      <div className="flex items-center gap-2 text-xl">
        <span>면접 Agent</span>
      </div>
      <Modal open={open} onCancel={() => setOpen(false)}>
        <AssessmentPopup />
      </Modal>
>>>>>>> Stashed changes
    </div>
  );
};

export default ChatHeader;
