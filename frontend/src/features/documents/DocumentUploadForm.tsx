import { FormEvent, useState } from 'react';

import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

interface UploadPayload {
  file: File;
  document_type: string;
  number?: string;
  document_date?: string;
}

interface DocumentUploadFormProps {
  onSubmit: (payload: UploadPayload) => Promise<unknown> | void;
  loading?: boolean;
}

export function DocumentUploadForm({ onSubmit, loading = false }: DocumentUploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [type, setType] = useState('invoice');
  const [number, setNumber] = useState('');
  const [docDate, setDocDate] = useState('');

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) return;

    await onSubmit({
      file,
      document_type: type,
      number: number || undefined,
      document_date: docDate || undefined,
    });

    setFile(null);
    setNumber('');
    setDocDate('');
    setType('invoice');
  };

  return (
    <form className="grid gap-3 rounded-2xl bg-white p-5 shadow-card ring-1 ring-slate-100 md:grid-cols-4" onSubmit={handleSubmit}>
      <Input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} required className="md:col-span-2" />
      <Input placeholder="Тип документа" value={type} onChange={(e) => setType(e.target.value)} />
      <Input placeholder="Номер" value={number} onChange={(e) => setNumber(e.target.value)} />
      <Input type="date" value={docDate} onChange={(e) => setDocDate(e.target.value)} />
      <div className="md:col-span-4 md:justify-self-end">
        <Button type="submit" disabled={loading || !file}>
          Загрузить документ
        </Button>
      </div>
    </form>
  );
}
