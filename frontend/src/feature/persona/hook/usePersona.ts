import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Api } from '../../../shared/Api';
import type { PersonaDTO, PersonaInputDTO } from '../../../shared/type';

const usePersona = () => {
  return useQuery({
    queryKey: ['personaList'],
    queryFn: () => Api.GET<PersonaDTO[]>('/persona/list'),
  });
};

const usePersonaMutation = () => {
  const queryClient = useQueryClient();
  const { mutateAsync: addPersona } = useMutation({
    mutationFn: (persona: PersonaInputDTO) =>
      Api.POST<PersonaInputDTO, PersonaDTO[]>('/persona', persona),
    onSuccess: (data) => {
      queryClient.setQueryData(['personaList'], data);
    },
  });

  const { mutateAsync: deletePersona } = useMutation({
    mutationFn: (personaId: string) =>
      Api.DELETE<PersonaDTO[]>(`/persona/${personaId}`),
    onSuccess: (data) => {
      queryClient.setQueryData(['personaList'], data);
    },
  });

  return { addPersona, deletePersona };
};

export { usePersona, usePersonaMutation };
