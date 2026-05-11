import { useMemo, useState, type FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Pencil, Trash2, Plus, Search, KeyRound } from 'lucide-react';

import { adminApi, type Role, type User } from '../api/admin';
import { Modal } from '../components/Modal';
import { ApiError } from '../api/client';
import { useAuth } from '../auth/useAuth';

const ROLE_LABEL: Record<Role, string> = {
  superadmin: 'Superadmin',
  admin: 'Admin',
  user: 'User',
};

export default function UsersPage() {
  const { user: me, impersonate } = useAuth();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const isSuperadmin = me?.role === 'superadmin';

  const [filterCompanyId, setFilterCompanyId] = useState<string>('');
  const [search, setSearch] = useState('');

  const usersQuery = useQuery({
    queryKey: ['admin', 'users', filterCompanyId || 'all'],
    queryFn: () => adminApi.listUsers(filterCompanyId || undefined),
  });
  const companiesQuery = useQuery({
    queryKey: ['admin', 'companies'],
    queryFn: adminApi.listCompanies,
    enabled: isSuperadmin,
  });

  const filtered = useMemo(() => {
    if (!usersQuery.data) return [];
    const q = search.trim().toLowerCase();
    if (!q) return usersQuery.data;
    return usersQuery.data.filter(
      (u) =>
        u.email.toLowerCase().includes(q) ||
        (u.full_name ?? '').toLowerCase().includes(q),
    );
  }, [usersQuery.data, search]);

  const [editing, setEditing] = useState<User | null>(null);
  const [creating, setCreating] = useState(false);

  const onChanged = () => qc.invalidateQueries({ queryKey: ['admin', 'users'] });
  const companyName = (id: string) =>
    companiesQuery.data?.find((c) => c.id === id)?.name ?? id.slice(0, 8);

  const onImpersonate = async (u: User) => {
    if (!window.confirm(`Войти от имени «${u.email}»?`)) return;
    try {
      await impersonate(u.id);
      navigate('/', { replace: true });
    } catch (e) {
      alert(e instanceof ApiError ? e.message : 'Ошибка');
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4 gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Поиск:"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100 w-64"
            />
          </div>
          {isSuperadmin && companiesQuery.data && (
            <select
              value={filterCompanyId}
              onChange={(e) => setFilterCompanyId(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
            >
              <option value="">Все компании</option>
              {companiesQuery.data.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          )}
        </div>
        <div className="text-sm text-slate-500">
          Всего: {filtered.length}
          {search && usersQuery.data && filtered.length !== usersQuery.data.length
            ? ` из ${usersQuery.data.length}` : ''}
        </div>
        <button
          onClick={() => setCreating(true)}
          className="inline-flex items-center gap-2 px-3 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm font-medium"
        >
          <Plus size={14} /> Создать
        </button>
      </div>

      {usersQuery.isLoading && <p className="text-slate-500">Загрузка…</p>}
      {usersQuery.error && (
        <p className="text-rose-600">Ошибка: {String((usersQuery.error as Error).message)}</p>
      )}

      {usersQuery.data && (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-2.5 font-semibold text-slate-700">Email</th>
                <th className="text-left px-4 py-2.5 font-semibold text-slate-700">ФИО</th>
                <th className="text-left px-4 py-2.5 font-semibold text-slate-700">Роль</th>
                {isSuperadmin && (
                  <th className="text-left px-4 py-2.5 font-semibold text-slate-700">Компания</th>
                )}
                <th className="w-72"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={isSuperadmin ? 5 : 4} className="text-center text-slate-400 py-8">
                    {search ? 'Ничего не найдено' : 'Пользователи не найдены'}
                  </td>
                </tr>
              )}
              {filtered.map((u) => {
                const isSelf = u.id === me?.user_id;
                return (
                  <tr key={u.id} className="hover:bg-slate-50">
                    <td className="px-4 py-2.5 font-medium text-slate-800">{u.email}</td>
                    <td className="px-4 py-2.5 text-slate-600">{u.full_name ?? '—'}</td>
                    <td className="px-4 py-2.5">
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        {ROLE_LABEL[u.role]}
                      </span>
                    </td>
                    {isSuperadmin && (
                      <td className="px-4 py-2.5 text-slate-500 text-xs">{companyName(u.company_id)}</td>
                    )}
                    <td className="px-4 py-2.5 text-right whitespace-nowrap">
                      {isSuperadmin && !isSelf && (
                        <button
                          onClick={() => onImpersonate(u)}
                          className="inline-flex items-center gap-1 text-teal-600 hover:text-teal-800 text-xs mr-3"
                        >
                          <KeyRound size={12} /> Войти
                        </button>
                      )}
                      <button
                        onClick={() => setEditing(u)}
                        className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 text-xs mr-3"
                      >
                        <Pencil size={12} /> Изменить
                      </button>
                      {!isSelf && (
                        <DeleteButton id={u.id} email={u.email} onDone={onChanged} />
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {creating && (
        <UserModal
          title="Создать пользователя"
          onClose={() => setCreating(false)}
          onDone={onChanged}
          companies={companiesQuery.data ?? []}
          isSuperadmin={isSuperadmin}
        />
      )}
      {editing && (
        <UserModal
          title={`Изменить ${editing.email}`}
          user={editing}
          onClose={() => setEditing(null)}
          onDone={onChanged}
          companies={companiesQuery.data ?? []}
          isSuperadmin={isSuperadmin}
        />
      )}
    </div>
  );
}

function DeleteButton({ id, email, onDone }: { id: string; email: string; onDone: () => void }) {
  const mutation = useMutation({
    mutationFn: () => adminApi.deleteUser(id),
    onSuccess: onDone,
  });
  const onClick = () => {
    if (window.confirm(`Удалить пользователя «${email}»?`)) {
      mutation.mutate();
    }
  };
  return (
    <button
      onClick={onClick}
      disabled={mutation.isPending}
      className="inline-flex items-center gap-1 text-rose-600 hover:text-rose-700 text-xs disabled:opacity-50"
    >
      <Trash2 size={12} /> Удалить
    </button>
  );
}

function UserModal({
  title,
  user,
  onClose,
  onDone,
  companies,
  isSuperadmin,
}: {
  title: string;
  user?: User;
  onClose: () => void;
  onDone: () => void;
  companies: { id: string; name: string }[];
  isSuperadmin: boolean;
}) {
  const [email, setEmail] = useState(user?.email ?? '');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState(user?.full_name ?? '');
  const [role, setRole] = useState<Role>(user?.role ?? 'user');
  const [companyId, setCompanyId] = useState(user?.company_id ?? '');
  const [err, setErr] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => {
      if (user) {
        const patch: { email?: string; password?: string; role?: Role; full_name?: string | null } = {
          email,
          role,
          full_name: fullName || null,
        };
        if (password) patch.password = password;
        return adminApi.updateUser(user.id, patch);
      }
      return adminApi.createUser({
        email,
        password,
        role,
        full_name: fullName || null,
        company_id: isSuperadmin ? companyId : undefined,
      });
    },
    onSuccess: () => {
      onDone();
      onClose();
    },
    onError: (e) => setErr(e instanceof ApiError ? e.message : 'Ошибка сервера'),
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    setErr(null);
    mutation.mutate();
  };

  return (
    <Modal
      title={title}
      onClose={onClose}
      size="lg"
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-slate-200 rounded-lg text-sm"
          >
            Отмена
          </button>
          <button
            type="submit"
            form="user-form"
            disabled={mutation.isPending}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm disabled:opacity-60"
          >
            {mutation.isPending ? 'Сохранение…' : 'Сохранить'}
          </button>
        </>
      }
    >
      <form id="user-form" onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
            autoFocus={!user}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Пароль {user && <span className="text-slate-400 text-xs">(оставь пустым чтобы не менять)</span>}
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required={!user}
            minLength={6}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">ФИО</label>
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Роль</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as Role)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
            {isSuperadmin && <option value="superadmin">Superadmin</option>}
          </select>
        </div>

        {!user && isSuperadmin && (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Компания</label>
            <select
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              required
              className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
            >
              <option value="">— выберите —</option>
              {companies.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        )}

        {err && <p className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{err}</p>}
      </form>
    </Modal>
  );
}
