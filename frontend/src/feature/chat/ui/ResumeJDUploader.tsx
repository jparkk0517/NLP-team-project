import type { FormEvent } from 'react';
import { useUploadContext } from '../hook/useContext';

interface IResumeJDUploader {
  refetch: () => void;
}
const ResumeJDUploader = ({ refetch }: IResumeJDUploader) => {
  const { mutateAsync: uploadResume } = useUploadContext();
  const handleSubmit = async (e: FormEvent<Element>) => {
    try {
      e.preventDefault();
      const target = e.target as HTMLFormElement;
      const resumeFile =
        target.querySelector<HTMLInputElement>('#resume')?.files?.[0];
      const jdFile = target.querySelector<HTMLInputElement>('#jd')?.files?.[0];

      if (resumeFile && jdFile) {
        await uploadResume({
          resumeFile,
          jdFile,
        });
        refetch();
      } else {
        console.error('Both resume and JD files must be provided.');
      }
    } catch (error) {
      console.error(error);
    }
  };
  return (
    <form onSubmit={handleSubmit}>
      <div className='p-4'>
        <label htmlFor='resume' className='text-sm text-gray-500'>
          Resume
        </label>
        <input
          id='resume'
          type='file'
          multiple
          className='block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100'
        />
      </div>
      <div className='p-4'>
        <label htmlFor='jd' className='text-sm text-gray-500'>
          JD
        </label>
        <input
          id='jd'
          type='file'
          multiple
          className='block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100'
        />
      </div>
      <button
        type='submit'
        className='bg-violet-500 text-white px-4 py-2 rounded-md'>
        업로드
      </button>
    </form>
  );
};

export default ResumeJDUploader;
