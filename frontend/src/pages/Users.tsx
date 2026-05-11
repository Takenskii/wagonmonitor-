import { useState, type FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { adminApi, type Role, type User } from '../api/admin';
import { Modal } from '../components/Modal';
import { KebabMenu, MenuItem } from '../components/KebabMenu';
import { ApiError } from '../api/client';
import { useAuth } from '../auth/useAuth';

const ROLE_LABEL: Record<Role, string> = {
  superadmin: 'Superadmin',
  admin: 'Admin',
  user: 'User',
};

const ROLE_PILL: Record<Role, string> = {
  superadmin: 'bg-rose-50 text-rose-700 border border-rose-200',
  admin: 'bg-blue-50 text-blue-700 border border-blue-200',
  user: 'bg-slate-100 text-slate-700 border border-slate-200',
};

const ROLE_AVATAR: Record<Role, string> = {
  superadmin: 'from-rose-200 to-rose-400',
  admin: 'from-blue-200 to-blue-400',
  user: 'from-slate-200 to-slate-400',
};

export default function UsersPage() {
  const { user: me } = useAuth();
  const qc = useQueryClient();
  const isSuperadmin = me?.role === 'superadmin';

  const [filterCompanyId, setFilterCompanyId] = useState<string>('');

  const usersQuery = useQuery({
    queryKey: ['admin', 'users', filterCompanyId || 'all'],
    queryFn: () => adminApi.listUsers(filterCompanyId || undefined),
  });
  const companiesQuery = useQuery({
    queryKey: ['admin', 'companies'],
    queryFn: adminApi.listCompanies,
    enabled: isSuperadmin,
  });

  const [editing, setEditing] = useState<User | null>(null);
  const [creating, setCreating] = useState(false);

  const onChanged = () => qc.invalidateQueries({ queryKey: ['admin', 'users'] });

  const companyName = (id: string) =>
    companiesQuery.data?.find((c) => c.id === id)?.name ?? id.slice(0, 8);

  return (
    <div className="p-8 max-w-6xl">
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => setCreating(true)}
          className="inline-flex items-center gap-2 px-4 py-2 border border-blue-200 bg-blue-50/60 text-blue-700 rounded-xl hover:bg-blue-100 text-sm font-medium transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M7 1v12M1 7h12" />
          </svg>
          Создать пользователя
        </button>

        {isSuperadmin && companiesQuery.data && (
          <select
            value={filterCompanyId}
            onChange={(e) => setFilterCompanyId(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-xl text-sm bg-white"
          >
            <option value="">Все компании</option>
            {companiesQuery.data.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        )}
      </div>

      <h2 className="text-xl font-bold text-slate-900 mb-4">Пользователи</h2>

      {usersQuery.isLoading && <p className="text-slate-500">Загрузка…</p>}
      {usersQuery.error && (
        <p className="text-rose-600">Ошибка: {String((usersQuery.error as Error).message)}</p>
      )}

      {usersQuery.data && usersQuery.data.length === 0 && (
        <p className="text-slate-400 text-center py-12">Пользователи не найдены</p>
      )}

      {usersQuery.data && usersQuery.data.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {usersQuery.data.map((u) => (
            <UserCard
              key={u.id}
              user={u}
              isSelf={u.id === me?.user_id}
              isSuperadmin={isSuperadmin}
              companyName={companyName(u.company_id)}
              onEdit={() => setEditing(u)}
              onChanged={onChanged}
            />
          ))}
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

function UserCard({
  user,
  isSelf,
  isSuperadmin,
  companyName,
  onEdit,
  onChanged,
}: {
  user: User;
  isSelf: boolean;
  isSuperadmin: boolean;
  companyName: string;
  onEdit: () => void;
  onChanged: () => void;
}) {
  const deleteMut = useMutation({
    mutationFn: () => adminApi.deleteUser(user.id),
    onSuccess: onChanged,
  });

  const onDelete = () => {
    if (window.confirm(`Удалить пользователя «${user.email}»?`)) {
      deleteMut.mutate();
    }
  };

  const initial = (user.full_name ?? user.email).charAt(0).toUpperCase();

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div
          className={`w-12 h-12 rounded-xl bg-gradient-to-br ${ROLE_AVATAR[user.role]} shrink-0 flex items-center justify-center text-white font-bold`}
        >
          {initial}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 truncate" title={user.email}>
            {user.email}
          </h3>
          <p className="text-xs text-slate-500 truncate">
            {user.full_name ?? '— ФИО не указано —'}
          </p>
        </div>
        <KebabMenu>
          <MenuItem onClick={onEdit}>Изменить</MenuItem>
          {!isSelf && (
            <MenuItem onClick={onDelete} danger>Удалить</MenuItem>
          )}
        </KebabMenu>
      </div>

      <div className="flex items-center gap-2 mt-4 text-xs">
        <span className={`px-2 py-0.5 rounded-full font-semibold ${ROLE_PILL[user.role]}`}>
          {ROLE_LABEL[user.role]}
        </span>
        {isSuperadmin && (
          <span className="text-slate-500 truncate" title={companyName}>
            · {companyName}
          </span>
        )}
        {isSelf && (
          <span className="text-blue-600 font-medium">· вы</span>
        )}
      </div>
    </div>
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
            className="px-4 py-2 border border-slate-200 rounded-xl text-sm"
          >
            Отмена
          </button>
          <button
            type="submit"
            form="user-form"
            disabled={mutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm disabled:opacity-60"
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
            className="w-full px-3 py-2 border border-slate-200 rounded-xl outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
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
            className="w-full px-3 py-2 border border-slate-200 rounded-xl outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">ФИО</label>
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-xl outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Роль</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as Role)}
            className="w-full px-3 py-2 border border-slate-200 rounded-xl outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
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
              className="w-full px-3 py-2 border border-slate-200 rounded-xl outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
            >
              <option value="">— выберите —</option>
              {companies.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        )}

        {err && <p className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-xl">{err}</p>}
      </form>
    </Modal>
  );
}
