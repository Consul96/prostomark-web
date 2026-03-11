import { FormEvent, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

import { authApi } from '../../api/auth';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { useAuthStore } from '../../store/authStore';

export function LoginPage() {
  const navigate = useNavigate();
  const setSession = useAuthStore((state) => state.setSession);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const mutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (response) => {
      setSession(response.tokens.access_token, response.tokens.refresh_token, response.user);
      toast.success('Вход выполнен');
      navigate('/app/dashboard');
    },
    onError: () => {
      toast.error('Ошибка авторизации');
    },
  });

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    mutation.mutate({ email, password });
  };

  return (
    <div className="mx-auto max-w-md rounded-2xl bg-white p-6 shadow-card ring-1 ring-slate-100">
      <h1 className="text-2xl font-bold">Вход</h1>
      <form className="mt-6 space-y-4" onSubmit={submit}>
        <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <Input type="password" placeholder="Пароль" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <Button className="w-full" type="submit" disabled={mutation.isPending}>
          Войти
        </Button>
      </form>
      <p className="mt-4 text-sm text-slate-600">
        Нет аккаунта?{' '}
        <Link to="/register" className="text-brand-700">
          Зарегистрироваться
        </Link>
      </p>
    </div>
  );
}
