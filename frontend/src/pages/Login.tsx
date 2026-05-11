import { useState, type FormEvent } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { useAuth } from '../auth/useAuth';
import { ApiError } from '../api/client';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname ?? '/';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError('Неверный логин или пароль');
      } else {
        setError('Ошибка сервера. Попробуйте позже.');
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-sm bg-white p-8 rounded-2xl shadow-sm border border-slate-200 space-y-4"
      >
        <h1 className="text-2xl font-bold text-slate-900">Wagon Monitor</h1>
        <p className="text-sm text-slate-500">Войдите в систему</p>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-brand-primary focus:ring-2 focus:ring-brand-primary/20"
            autoComplete="username"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Пароль</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-brand-primary focus:ring-2 focus:ring-brand-primary/20"
            autoComplete="current-password"
          />
        </div>

        {error && (
          <p className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{error}</p>
        )}

        <button
          type="submit"
          disabled={busy}
          className="w-full py-2.5 bg-brand-primary text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60"
        >
          {busy ? 'Вход…' : 'Войти'}
        </button>
      </form>
    </div>
  );
}
