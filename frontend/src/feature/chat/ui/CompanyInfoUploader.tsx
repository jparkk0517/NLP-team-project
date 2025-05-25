import { useUploadCompanyInfo } from '../hook/useContext';

interface ICompanyInfoUploader {
  refetch: () => void;
}
const CompanyInfoUploader = ({ refetch }: ICompanyInfoUploader) => {
  const { mutateAsync: uploadCompanyInfo } = useUploadCompanyInfo();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    try {
      const companyFiles = e.target.files;
      if (companyFiles) {
        await uploadCompanyInfo({ companyFiles: Array.from(companyFiles) });
        refetch();
        e.target.value = ''; // 업로드 후 input 필드 비우기
      } else {
        console.error('Company files must be provided.');
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      <label htmlFor='companyFiles' className='text-sm text-gray-500'>
        회사 정보 파일
      </label>
      <input
        id='companyFiles'
        type='file'
        multiple
        onChange={handleFileChange}
        className='block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100'
      />
    </div>
  );
};

export default CompanyInfoUploader;
