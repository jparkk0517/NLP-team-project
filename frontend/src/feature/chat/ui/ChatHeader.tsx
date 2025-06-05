import { MdOutlineAssessment } from 'react-icons/md';
import AssessmentPopup from '../../assessment/ui/AssessmentPopup';
import { Modal } from 'antd';
import { useState } from 'react';

const ChatHeader = () => {
  const [open, setOpen] = useState(false);
  const handleAssessment = () => {
    setOpen(true);
  };
  return (
    <div className='relative flex items-center justify-around p-4 h-[5%] border-b-2 border-gray-300'>
      <div className='absolute left-4 top-1/2 -translate-y-1/2 text-2xl cursor-pointer'>
        <div className='flex items-center gap-2' onClick={handleAssessment}>
          <MdOutlineAssessment className='text-1xl' />
          <span className='text-sm'>평가</span>
        </div>
      </div>
      <div className='flex items-center gap-2 text-xl'>
        <span>면접 Agent</span>
      </div>
      <Modal open={open} onCancel={() => setOpen(false)}>
        <AssessmentPopup />
      </Modal>
    </div>
  );
};

export default ChatHeader;
