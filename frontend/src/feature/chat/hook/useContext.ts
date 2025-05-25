import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

const useCheckContext = () => {
  return useQuery<{
    message: string;
    uploaded: boolean;
  }>({
    queryKey: ['check_context'],
    queryFn: () => {
      return fetch('http://localhost:8000/check_context').then((res) =>
        res.json()
      );
    },
  });
};

const useUploadContext = () => {
  return useMutation({
    mutationFn: (context: { resumeFile: File; jdFile: File }) => {
      const formData = new FormData();
      formData.append('resume_file', context.resumeFile);
      formData.append('jd_file', context.jdFile);

      return fetch('http://localhost:8000/context_files', {
        method: 'POST',
        body: formData,
      }).then((res) => res.json());
    },
  });
};

const useDeleteContext = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => {
      return fetch('http://localhost:8000/context', { method: 'DELETE' });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['check_context'] });
    },
  });
};

const useUploadCompanyInfo = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (context: { companyFiles: File[] }) => {
      const formData = new FormData();
      context.companyFiles.forEach((file) => {
        formData.append('files', file);
      });

      return fetch('http://localhost:8000/upload_docs', {
        method: 'POST',
        body: formData,
      }).then((res) => res.json());
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['company_info_files'] });
    },
  });
};

const useGetCompanyInfoFiles = () => {
  return useQuery<{ files: { id: string; filename: string }[] }>({
    queryKey: ['company_info_files'],
    queryFn: () =>
      fetch('http://localhost:8000/company_info_files').then((res) =>
        res.json()
      ),
  });
};

const useDeleteCompanyInfoFile = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (docId: string) => {
      return fetch(`http://localhost:8000/company_info_file/${docId}`, {
        method: 'DELETE',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['company_info_files'] });
    },
  });
};
const useStoreInit = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => {
      return fetch('http://localhost:8000/store_init', { method: 'POST' });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['check_context'] });
      queryClient.invalidateQueries({ queryKey: ['company_info_files'] });
    },
  });
};

export {
  useCheckContext,
  useUploadContext,
  useDeleteContext,
  useUploadCompanyInfo,
  useGetCompanyInfoFiles,
  useDeleteCompanyInfoFile,
  useStoreInit,
};
