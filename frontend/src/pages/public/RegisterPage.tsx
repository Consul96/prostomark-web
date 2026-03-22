import { FormEvent, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

import { authApi } from '../../api/auth';
import { getApiErrorMessage } from '../../api/errors';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { useAuthStore } from '../../store/authStore';

export function RegisterPage() {
  const navigate = useNavigate();
  const setSession = useAuthStore((state) => state.setSession);

  const [companyName, setCompanyName] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const mutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: (response) => {
      setSession(response.tokens.access_token, response.tokens.refresh_token, response.user);
      toast.success('Регистрация завершена');
      navigate('/app/dashboard');
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, 'Не удалось зарегистрироваться'));
    },
  });

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    mutation.mutate({
      company_name: companyName,
      first_name: firstName,
      last_name: lastName,
      email,
      password,
    });
  };

  return (
    <div className="mx-auto max-w-xl rounded-2xl bg-white p-6 shadow-card ring-1 ring-slate-100">
      <h1 className="text-2xl font-bold">Регистрация</h1>
      <form className="mt-6 grid gap-4 md:grid-cols-2" onSubmit={submit}>
        <Input className="md:col-span-2" placeholder="Название компании" value={companyName} onChange={(e) => setCompanyName(e.target.value)} required />
        <Input placeholder="Имя" value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
        <Input placeholder="Фамилия" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
        <Input className="md:col-span-2" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <Input className="md:col-span-2" type="password" placeholder="Пароль" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
        <Button className="md:col-span-2" type="submit" disabled={mutation.isPending}>
          Создать аккаунт
        </Button>
      </form>
      <p className="mt-4 text-sm text-slate-600">
        Уже есть аккаунт?{' '}
        <Link to="/login" className="text-brand-700">
          Войти
        </Link>
      </p>
    </div>
  );
}
