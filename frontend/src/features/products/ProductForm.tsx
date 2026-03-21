import { FormEvent, useState } from 'react';

import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

interface ProductFormProps {
  onSubmit: (payload: { name: string; brand?: string; gtin?: string; article?: string }) => Promise<unknown> | void;
  loading?: boolean;
}

export function ProductForm({ onSubmit, loading = false }: ProductFormProps) {
  const [name, setName] = useState('');
  const [brand, setBrand] = useState('');
  const [gtin, setGtin] = useState('');
  const [article, setArticle] = useState('');

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim()) return;

    await onSubmit({ name, brand, gtin, article });
    setName('');
    setBrand('');
    setGtin('');
    setArticle('');
  };

  return (
    <form className="grid gap-3 rounded-2xl bg-white p-5 shadow-card ring-1 ring-slate-100 md:grid-cols-5" onSubmit={handleSubmit}>
      <Input placeholder="Название" value={name} onChange={(e) => setName(e.target.value)} required className="md:col-span-2" />
      <Input placeholder="Бренд" value={brand} onChange={(e) => setBrand(e.target.value)} />
      <Input placeholder="GTIN" value={gtin} onChange={(e) => setGtin(e.target.value)} />
      <Input placeholder="Артикул" value={article} onChange={(e) => setArticle(e.target.value)} />
      <div className="md:col-span-5 md:justify-self-end">
        <Button type="submit" disabled={loading}>
          Добавить товар
        </Button>
      </div>
    </form>
  );
}
