import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { calculationsApi } from '../../api/calculations';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';

interface CalcItem {
  name: string;
  qty: number;
  price: number;
}

export function CalculatorPage() {
  const [items, setItems] = useState<CalcItem[]>([{ name: 'Услуга', qty: 1, price: 0 }]);

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => calculationsApi.create(payload),
    onSuccess: (result) => {
      toast.success(`Расчет сохранен: ${result.total_amount} ${result.currency}`);
    },
    onError: () => toast.error('Ошибка расчета'),
  });

  const updateItem = (index: number, patch: Partial<CalcItem>) => {
    setItems((prev) => prev.map((item, i) => (i === index ? { ...item, ...patch } : item)));
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Калькулятор услуг</h1>
      <Card>
        <div className="space-y-3">
          {items.map((item, index) => (
            <div key={index} className="grid gap-3 md:grid-cols-3">
              <Input value={item.name} onChange={(e) => updateItem(index, { name: e.target.value })} placeholder="Название" />
              <Input
                type="number"
                value={item.qty}
                onChange={(e) => updateItem(index, { qty: Number(e.target.value) })}
                placeholder="Количество"
              />
              <Input
                type="number"
                value={item.price}
                onChange={(e) => updateItem(index, { price: Number(e.target.value) })}
                placeholder="Цена"
              />
            </div>
          ))}
        </div>

        <div className="mt-4 flex gap-3">
          <Button variant="secondary" onClick={() => setItems((prev) => [...prev, { name: '', qty: 1, price: 0 }])}>
            Добавить строку
          </Button>
          <Button onClick={() => mutation.mutate({ items })} disabled={mutation.isPending}>
            Рассчитать и сохранить
          </Button>
        </div>
      </Card>
    </div>
  );
}
