import {
  useDeleteCompanyInfoFile,
  useGetCompanyInfoFiles,
} from '../hook/useContext';

const CompanyInfoFileList = () => {
  const { data } = useGetCompanyInfoFiles();
  const { mutateAsync: deleteCompanyInfoFile } = useDeleteCompanyInfoFile();
  const handleDelete = async (docId: string) => {
    await deleteCompanyInfoFile(docId);
  };
  return (
    <div>
      awefewf
      {data?.files.map((file) => (
        <div className='flex items-center gap-2' key={file.id}>
          <span>{file.filename}</span>
          <button
            className='bg-red-500 text-white px-4 py-2 rounded-md'
            onClick={() => handleDelete(file.id)}>
            삭제
          </button>
        </div>
      ))}
    </div>
  );
};

export default CompanyInfoFileList;
