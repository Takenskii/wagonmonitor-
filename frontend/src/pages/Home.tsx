import { useQuery } from '@tanstack/react-query';

import { authApi } from '../api/auth';
import { useAuth } from '../auth/useAuth';

export default function HomePage() {
  const { user, logout } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ['me'],
    queryFn: authApi.me,
    staleTime: 60_000,
  });

  return (
    <div className="min-h-screen p-8 bg-slate-50">
      <div className="max-w-3xl mx-auto bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold text-slate-900">Wagon Monitor</h1>
          <button
            onClick={logout}
            className="text-sm text-rose-600 hover:text-rose-700"
          >
            Выйти
          </button>
        </div>

        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-2">
          Идентичность из JWT (localStorage)
        </h2>
        <pre className="text-xs bg-slate-50 border border-slate-200 rounded-lg p-3 overflow-auto mb-6">
          {JSON.stringify(user, null, 2)}
        </pre>

        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-2">
          /api/v1/auth/me (свежий запрос)
        </h2>
        {isLoading && <p className="text-sm text-slate-500">Загрузка…</p>}
        {error && (
          <p className="text-sm text-rose-600">Ошибка: {String((error as Error).message)}</p>
        )}
        {data && (
          <pre className="text-xs bg-slate-50 border border-slate-200 rounded-lg p-3 overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
