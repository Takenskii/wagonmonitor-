import { useMemo, useState, type FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Pencil, Trash2, Plus, Search } from 'lucide-react';

import { adminApi, type Company } from '../api/admin';
import { Modal } from '../components/Modal';
import { ApiError } from '../api/client';

export default function CompaniesPage() {
  const qc = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ['admin', 'companies'],
    queryFn: adminApi.listCompanies,
  });

  const [editing, setEditing] = useState<Company | null>(null);
  const [creating, setCreating] = useState(false);
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = search.trim().toLowerCase();
    if (!q) return data;
    return data.filter((c) => c.name.toLowerCase().includes(q));
  }, [data, search]);

  const onChanged = () => qc.invalidateQueries({ queryKey: ['admin', 'companies'] });

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4 gap-4 flex-wrap">
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
        <div className="text-sm text-slate-500">
          Всего: {filtered.length}
          {search && data && search.length > 0 && filtered.length !== data.length
            ? ` из ${data.length}` : ''}
        </div>
        <button
          onClick={() => setCreating(true)}
          className="inline-flex items-center gap-2 px-3 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm font-medium"
        >
          <Plus size={14} /> Создать
        </button>
      </div>

      {isLoading && <p className="text-slate-500">Загрузка…</p>}
      {error && (
        <p className="text-rose-600">Ошибка: {String((error as Error).message)}</p>
      )}

      {data && (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-2.5 font-semibold text-slate-700">Название</th>
                <th className="text-left px-4 py-2.5 font-semibold text-slate-700">Создано</th>
                <th className="w-40"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={3} className="text-center text-slate-400 py-8">
                    {search ? 'Ничего не найдено' : 'Компании не созданы'}
                  </td>
                </tr>
              )}
              {filtered.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2.5 font-medium text-slate-800">{c.name}</td>
                  <td className="px-4 py-2.5 text-slate-500 text-xs">
                    {new Date(c.created_at).toLocaleDateString('ru-RU')}
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <button
                      onClick={() => setEditing(c)}
                      className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 text-xs mr-3"
                    >
                      <Pencil size={12} /> Изменить
                    </button>
                    <DeleteButton id={c.id} name={c.name} onDone={onChanged} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
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

function DeleteButton({ id, name, onDone }: { id: string; name: string; onDone: () => void }) {
  const mutation = useMutation({
    mutationFn: () => adminApi.deleteCompany(id),
    onSuccess: onDone,
  });
  const onClick = () => {
    if (
      window.confirm(
        `Удалить компанию «${name}»?\nВсе её пользователи будут удалены вместе с ней.`,
      )
    ) {
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
            className="px-4 py-2 border border-slate-200 rounded-lg text-sm"
          >
            Отмена
          </button>
          <button
            type="submit"
            form="company-form"
            disabled={mutation.isPending}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm disabled:opacity-60"
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
            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
            autoFocus
          />
        </div>
        {err && <p className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{err}</p>}
      </form>
    </Modal>
  );
}
