import {
  useCheckContext,
  useDeleteContext,
  useStoreInit,
} from '../hook/useContext';
import CompanyInfoFileList from './CompanyInfoFileList';
import CompanyInfoUploader from './CompanyInfoUploader';

import ResumeJDUploader from './ResumeJDUploader';

const ChatHeader = () => {
  const { data, refetch } = useCheckContext();
  const { mutateAsync: deleteResume } = useDeleteContext();
  const { mutateAsync: storeInit } = useStoreInit();
  const handleDelete = async () => {
    try {
      await deleteResume();
      refetch();
    } catch (error) {
      console.error(error);
    }
  };
  const handleStoreInit = async () => {
    try {
      await storeInit();
      refetch();
    } catch (error) {
      console.error(error);
    }
  };
  return (
    <>
      <div className='flex justify-between items-center'>
        <h1 className='text-2xl font-bold'>Chat</h1>
        <div>
          <button
            className='bg-blue-500 text-white px-4 py-2 rounded-md'
            onClick={handleStoreInit}>
            초기화
          </button>
          {data?.uploaded === true && (
            <button
              className='bg-red-500 text-white px-4 py-2 rounded-md'
              onClick={handleDelete}>
              이력서, JD 삭제
            </button>
          )}
        </div>
      </div>
      {!data?.uploaded && <ResumeJDUploader refetch={refetch} />}
      <CompanyInfoUploader refetch={refetch} />
      <CompanyInfoFileList />
    </>
  );
};

export default ChatHeader;
