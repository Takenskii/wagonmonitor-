import { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { MapPin, RefreshCw, Search, ChevronDown, Plus } from 'lucide-react';

import { dislocationsApi, type WagonDislocation } from '../api/dislocations';
import { AssignTrackingModal } from '../components/AssignTrackingModal';

type Status = 'active' | 'archived' | 'all';

const STATUS_LABEL: Record<Status, string> = {
  active: 'Активные',
  archived: 'Архив',
  all: 'Все',
};

function fmtDate(iso: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const hasTime = iso.includes('T') || /\d\d:\d\d/.test(iso);
  return hasTime
    ? d.toLocaleString('ru-RU', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
    : d.toLocaleDateString('ru-RU');
}

function fmtNum(n: number | null): string {
  if (n === null || n === undefined) return '—';
  return typeof n === 'number' ? n.toLocaleString('ru-RU') : String(n);
}

export default function DislocationPage() {
  const qc = useQueryClient();
  const [status, setStatus] = useState<Status>('active');
  const [search, setSearch] = useState('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['dislocations', status, search],
    queryFn: () =>
      dislocationsApi.list({
        status,
        search: search.trim() || undefined,
      }),
  });

  const wagons = data ?? [];

  // Уникальные группы из текущей выборки — для select'а в модалке
  const existingGroups = useMemo(() => {
    const map = new Map<string, string>();
    wagons.forEach((w) => {
      if (w.group_id && w.group_name) map.set(w.group_id, w.group_name);
    });
    return Array.from(map.entries()).map(([id, name]) => ({ id, name }));
  }, [wagons]);

  const [assignOpen, setAssignOpen] = useState(false);

  const onAssignSuccess = () => {
    qc.invalidateQueries({ queryKey: ['dislocations'] });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-slate-200 bg-white">
        <h1 className="flex items-center gap-2 font-semibold text-slate-800">
          <MapPin size={16} className="text-teal-600" />
          Слежение
        </h1>
        <RequestsMenu onAssign={() => setAssignOpen(true)} />
      </div>

      {/* Toolbar */}
      <div className="px-6 py-3 border-b border-slate-200 bg-white flex items-center gap-3 flex-wrap">
        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded transition-colors disabled:opacity-50"
          title="Обновить"
        >
          <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
        </button>

        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Поиск по № вагона/контейнера"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-3 py-1.5 border border-slate-300 rounded-lg text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100 w-72"
          />
        </div>

        <div className="flex gap-1">
          {(['active', 'archived', 'all'] as Status[]).map((s) => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                status === s
                  ? 'bg-teal-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {STATUS_LABEL[s]}
            </button>
          ))}
        </div>

        <div className="text-sm text-slate-500 ml-auto">Строк: {wagons.length}</div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto bg-slate-50">
        {isLoading && <p className="p-6 text-slate-500">Загрузка…</p>}
        {error && (
          <p className="p-6 text-rose-600">Ошибка: {String((error as Error).message)}</p>
        )}

        {data && wagons.length === 0 && (
          <div className="p-12 text-center">
            <p className="text-slate-400 mb-3">Нет вагонов на слежении.</p>
            <button
              onClick={() => setAssignOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm"
            >
              <Plus size={14} /> Поставить вагон на слежение
            </button>
          </div>
        )}

        {data && wagons.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs border-collapse">
              <thead className="bg-slate-100 sticky top-0">
                <tr>
                  {[
                    '№ вагона',
                    'Группа',
                    'Род вагона',
                    'Груж/Пор',
                    'Станция операции',
                    'Операция',
                    'Дата операции',
                    'Дорога дислокации',
                    'Назначение',
                    'Груз',
                    'Дней на станции',
                    'Статус',
                  ].map((h) => (
                    <th
                      key={h}
                      className="text-left px-3 py-2 font-semibold text-slate-700 border-b border-slate-300 whitespace-nowrap"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {wagons.map((w) => (
                  <Row key={w.track_id} w={w} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {assignOpen && (
        <AssignTrackingModal
          existingGroups={existingGroups}
          onClose={() => setAssignOpen(false)}
          onSuccess={onAssignSuccess}
        />
      )}
    </div>
  );
}

function RequestsMenu({ onAssign }: { onAssign: () => void }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 text-white rounded-lg text-sm hover:bg-slate-900"
      >
        Запросы
        <ChevronDown size={14} className={`transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-20 py-1 min-w-[240px]">
          <button
            onClick={() => {
              onAssign();
              setOpen(false);
            }}
            className="block w-full text-left px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
          >
            + Постановка на слежение
          </button>
          <button
            disabled
            className="block w-full text-left px-3 py-2 text-sm text-slate-400 cursor-not-allowed"
            title="Скоро"
          >
            − Снять со слежения
          </button>
          <div className="border-t border-slate-100 my-1" />
          <button
            disabled
            className="block w-full text-left px-3 py-2 text-sm text-slate-400 cursor-not-allowed"
            title="Скоро"
          >
            Добавить вагоны в группу
          </button>
          <button
            disabled
            className="block w-full text-left px-3 py-2 text-sm text-slate-400 cursor-not-allowed"
            title="Скоро"
          >
            Удалить вагоны из группы
          </button>
        </div>
      )}
    </div>
  );
}

function Row({ w }: { w: WagonDislocation }) {
  return (
    <tr className="hover:bg-slate-100 bg-white border-b border-slate-200">
      <td className="px-3 py-1.5 font-medium text-slate-800 whitespace-nowrap">{w.number}</td>
      <td className="px-3 py-1.5 text-slate-600">{w.group_name ?? <span className="text-slate-400">—</span>}</td>
      <td className="px-3 py-1.5">{w.car_type_name ?? '—'}</td>
      <td className="px-3 py-1.5">{w.is_full_name ?? '—'}</td>
      <td className="px-3 py-1.5">{w.oper_station_name ?? '—'}</td>
      <td className="px-3 py-1.5">{w.oper_name ?? '—'}</td>
      <td className="px-3 py-1.5 whitespace-nowrap">{fmtDate(w.oper_date)}</td>
      <td className="px-3 py-1.5">{w.disl_rw_name ?? '—'}</td>
      <td className="px-3 py-1.5">{w.dest_station_name ?? '—'}</td>
      <td className="px-3 py-1.5">{w.cargo_name ?? '—'}</td>
      <td className="px-3 py-1.5 text-right">{fmtNum(w.day_count_on_station)}</td>
      <td className="px-3 py-1.5">
        {w.active ? (
          <span className="inline-block px-2 py-0.5 rounded text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200">
            активно
          </span>
        ) : (
          <span className="inline-block px-2 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 border border-slate-200">
            архив
          </span>
        )}
      </td>
    </tr>
  );
}
