import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { productsApi } from '../../api/products';
import { Button } from '../../components/ui/Button';
import { ProductForm } from '../../features/products/ProductForm';
import { formatDate } from '../../shared/format';

export function ProductsPage() {
  const queryClient = useQueryClient();
  const { data: products = [], isLoading } = useQuery({ queryKey: ['products'], queryFn: productsApi.list });

  const createMutation = useMutation({
    mutationFn: productsApi.create,
    onSuccess: () => {
      toast.success('Товар создан');
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: () => toast.error('Не удалось создать товар'),
  });

  const deleteMutation = useMutation({
    mutationFn: productsApi.remove,
    onSuccess: () => {
      toast.success('Товар удален');
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: () => toast.error('Не удалось удалить товар'),
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Товары</h1>
      <ProductForm onSubmit={(payload) => createMutation.mutateAsync(payload)} loading={createMutation.isPending} />

      {isLoading ? (
        <p>Загрузка...</p>
      ) : (
        <div className="overflow-auto rounded-2xl bg-white shadow-card ring-1 ring-slate-100">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-4 py-3">Название</th>
                <th className="px-4 py-3">Бренд</th>
                <th className="px-4 py-3">GTIN</th>
                <th className="px-4 py-3">Создан</th>
                <th className="px-4 py-3">Действия</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id} className="border-t border-slate-100">
                  <td className="px-4 py-3">{product.name}</td>
                  <td className="px-4 py-3">{product.brand || '-'}</td>
                  <td className="px-4 py-3">{product.gtin || '-'}</td>
                  <td className="px-4 py-3">{formatDate(product.created_at)}</td>
                  <td className="px-4 py-3">
                    <Button variant="danger" onClick={() => deleteMutation.mutate(product.id)}>
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
