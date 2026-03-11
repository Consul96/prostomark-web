import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { documentsApi } from '../../api/documents';
import { Button } from '../../components/ui/Button';
import { DocumentUploadForm } from '../../features/documents/DocumentUploadForm';
import { formatDate } from '../../shared/format';

export function DocumentsPage() {
  const queryClient = useQueryClient();
  const { data: docs = [], isLoading } = useQuery({ queryKey: ['documents'], queryFn: documentsApi.list });

  const uploadMutation = useMutation({
    mutationFn: documentsApi.upload,
    onSuccess: () => {
      toast.success('Документ загружен');
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
    onError: () => toast.error('Ошибка загрузки документа'),
  });

  const deleteMutation = useMutation({
    mutationFn: documentsApi.remove,
    onSuccess: () => {
      toast.success('Документ удален');
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
    onError: () => toast.error('Ошибка удаления документа'),
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Документы</h1>

      <DocumentUploadForm onSubmit={(payload) => uploadMutation.mutateAsync(payload)} loading={uploadMutation.isPending} />

      {isLoading ? (
        <p>Загрузка...</p>
      ) : (
        <div className="overflow-auto rounded-2xl bg-white shadow-card ring-1 ring-slate-100">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-4 py-3">Файл</th>
                <th className="px-4 py-3">Тип</th>
                <th className="px-4 py-3">Статус</th>
                <th className="px-4 py-3">Дата</th>
                <th className="px-4 py-3">Действия</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc) => (
                <tr key={doc.id} className="border-t border-slate-100">
                  <td className="px-4 py-3">{doc.original_filename}</td>
                  <td className="px-4 py-3">{doc.document_type}</td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-slate-100 px-2 py-1 text-xs">{doc.status}</span>
                  </td>
                  <td className="px-4 py-3">{formatDate(doc.created_at)}</td>
                  <td className="px-4 py-3">
                    <Button variant="danger" onClick={() => deleteMutation.mutate(doc.id)}>
                      Удалить
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
