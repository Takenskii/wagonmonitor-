import { useQuery } from '@tanstack/react-query';

import { authApi } from '../api/auth';
import { useAuth } from '../auth/useAuth';

export default function HomePage() {
  const { user } = useAuth();
  const { data } = useQuery({
    queryKey: ['me'],
    queryFn: authApi.me,
    staleTime: 60_000,
  });

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Главная</h1>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
        <div>
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-2">
            Текущий пользователь
          </h2>
          <div className="text-slate-700">
            <div>
              <span className="text-slate-400">Email:</span> {user?.email}
            </div>
            <div>
              <span className="text-slate-400">ФИО:</span> {user?.full_name ?? '—'}
            </div>
            <div>
              <span className="text-slate-400">Роль:</span> {user?.role}
            </div>
            <div>
              <span className="text-slate-400">Компания:</span> {user?.company_name}
            </div>
          </div>
        </div>

        {data && (
          <details>
            <summary className="text-sm font-semibold text-slate-500 uppercase tracking-wide cursor-pointer">
              Raw /me ответ
            </summary>
            <pre className="mt-2 text-xs bg-slate-50 border border-slate-200 rounded-lg p-3 overflow-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}
