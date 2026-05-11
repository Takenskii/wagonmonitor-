import { useState, type FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { adminApi, type Company } from '../api/admin';
import { Modal } from '../components/Modal';
import { KebabMenu, MenuItem } from '../components/KebabMenu';
import { ApiError } from '../api/client';

export default function CompaniesPage() {
  const qc = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ['admin', 'companies'],
    queryFn: adminApi.listCompanies,
  });

  const [editing, setEditing] = useState<Company | null>(null);
  const [creating, setCreating] = useState(false);

  const onChanged = () => qc.invalidateQueries({ queryKey: ['admin', 'companies'] });

  return (
    <div className="p-8 max-w-6xl">
      <button
        onClick={() => setCreating(true)}
        className="inline-flex items-center gap-2 px-4 py-2 border border-blue-200 bg-blue-50/60 text-blue-700 rounded-xl hover:bg-blue-100 text-sm font-medium transition-colors mb-6"
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M7 1v12M1 7h12" />
        </svg>
        Создать компанию
      </button>

      <h2 className="text-xl font-bold text-slate-900 mb-4">Компании</h2>

      {isLoading && <p className="text-slate-500">Загрузка…</p>}
      {error && (
        <p className="text-rose-600">Ошибка: {String((error as Error).message)}</p>
      )}

      {data && data.length === 0 && (
        <p className="text-slate-400 text-center py-12">Компании не созданы</p>
      )}

      {data && data.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.map((c) => (
            <CompanyCard
              key={c.id}
              company={c}
              onEdit={() => setEditing(c)}
              onChanged={onChanged}
            />
          ))}
        </div>
      )}

      {creating && (
        <CompanyModal title="Создать компанию" onClose={() => setCreating(false)} onDone={onChanged} />
      )}
      {editing && (
        <CompanyModal
          title={`Изменить «${editing.name}»`}
          company={editing}
          onClose={() => setEditing(null)}
          onDone={onChanged}
        />
      )}
    </div>
  );
}

function CompanyCard({
  company,
  onEdit,
  onChanged,
}: {
  company: Company;
  onEdit: () => void;
  onChanged: () => void;
}) {
  const deleteMut = useMutation({
    mutationFn: () => adminApi.deleteCompany(company.id),
    onSuccess: onChanged,
  });

  const onDelete = () => {
    if (
      window.confirm(
        `Удалить компанию «${company.name}»?\nВсе её пользователи будут удалены вместе с ней.`,
      )
    ) {
      deleteMut.mutate();
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-200 to-blue-400 shrink-0" />
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 truncate" title={company.name}>
            {company.name}
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Создано {new Date(company.created_at).toLocaleDateString('ru-RU')}
          </p>
        </div>
        <KebabMenu>
          <MenuItem onClick={onEdit}>Изменить</MenuItem>
          <MenuItem onClick={onDelete} danger>Удалить</MenuItem>
        </KebabMenu>
      </div>
    </div>
  );
}

function CompanyModal({
  title,
  company,
  onClose,
  onDone,
}: {
  title: string;
  company?: Company;
  onClose: () => void;
  onDone: () => void;
}) {
  const [name, setName] = useState(company?.name ?? '');
  const [err, setErr] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      company
        ? adminApi.updateCompany(company.id, { name })
        : adminApi.createCompany({ name }),
    onSuccess: () => {
      onDone();
      onClose();
    },
    onError: (e) =>
      setErr(e instanceof ApiError ? e.message : 'Ошибка сервера'),
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
            form="company-form"
            disabled={mutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm disabled:opacity-60"
          >
            {mutation.isPending ? 'Сохранение…' : 'Сохранить'}
          </button>
        </>
      }
    >
      <form id="company-form" onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Название</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            minLength={1}
            maxLength={255}
            className="w-full px-3 py-2 border border-slate-200 rounded-xl outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
            autoFocus
          />
        </div>
        {err && <p className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-xl">{err}</p>}
      </form>
    </Modal>
  );
}
