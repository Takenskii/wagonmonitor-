/** Модалка «Постановка на слежение». */
import { useMemo, useState, type FormEvent } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Settings2 } from 'lucide-react';

import { trackingApi } from '../api/tracking';
import { Modal } from './Modal';
import { ApiError } from '../api/client';

// Список стран СНГ + Балтика (в оригинале берётся из справочника на бэке)
const TERRITORIES = [
  'Казахстан', 'Россия', 'Беларусь', 'Украина', 'Узбекистан',
  'Кыргызстан', 'Туркменистан', 'Таджикистан', 'Армения',
  'Азербайджан', 'Грузия', 'Молдова', 'Литва', 'Латвия', 'Эстония',
];

interface Props {
  existingGroups: { id: string; name: string }[];
  onClose: () => void;
  onSuccess: () => void;
}

type GroupChoice = 'none' | 'existing' | 'new';

export function AssignTrackingModal({ existingGroups, onClose, onSuccess }: Props) {
  const [wagonNumbersText, setWagonNumbersText] = useState('');
  const [territory, setTerritory] = useState('');
  const [removeOnRouteEnd, setRemoveOnRouteEnd] = useState(false);

  const [groupChoice, setGroupChoice] = useState<GroupChoice>('none');
  const [existingGroupId, setExistingGroupId] = useState(existingGroups[0]?.id ?? '');
  const [newGroupName, setNewGroupName] = useState('');

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [deferredStartAt, setDeferredStartAt] = useState('');
  const [autoRemoveAt, setAutoRemoveAt] = useState('');

  const [err, setErr] = useState<string | null>(null);

  const parsedNumbers = useMemo(() => {
    return wagonNumbersText
      .split(/[\s,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);
  }, [wagonNumbersText]);

  const mutation = useMutation({
    mutationFn: () =>
      trackingApi.assign({
        wagon_numbers: parsedNumbers,
        initial_territory: territory || null,
        remove_on_route_end: removeOnRouteEnd,
        group_id: groupChoice === 'existing' ? existingGroupId || null : null,
        new_group_name: groupChoice === 'new' ? newGroupName || null : null,
        deferred_start_at: deferredStartAt
          ? new Date(deferredStartAt).toISOString()
          : null,
        auto_remove_at: autoRemoveAt
          ? new Date(autoRemoveAt).toISOString()
          : null,
      }),
    onSuccess: () => {
      onSuccess();
      onClose();
    },
    onError: (e) =>
      setErr(e instanceof ApiError ? e.message : 'Ошибка сервера'),
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    setErr(null);
    if (parsedNumbers.length === 0) {
      setErr('Укажите хотя бы один номер вагона');
      return;
    }
    if (groupChoice === 'existing' && !existingGroupId) {
      setErr('Выберите группу');
      return;
    }
    if (groupChoice === 'new' && !newGroupName.trim()) {
      setErr('Введите название новой группы');
      return;
    }
    mutation.mutate();
  };

  return (
    <Modal
      title="Постановка на слежение"
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
            form="assign-form"
            disabled={mutation.isPending}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm disabled:opacity-60"
          >
            {mutation.isPending ? 'Применение…' : 'Применить'}
          </button>
        </>
      }
    >
      <form id="assign-form" onSubmit={onSubmit} className="space-y-4">
        {/* Номера вагонов */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Номера вагонов/контейнеров
          </label>
          <textarea
            value={wagonNumbersText}
            onChange={(e) => setWagonNumbersText(e.target.value)}
            placeholder="Введите номера через пробел, запятую или новую строку"
            rows={3}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100 font-mono text-sm"
            autoFocus
          />
          {parsedNumbers.length > 0 && (
            <p className="text-xs text-slate-500 mt-1">
              Распознано номеров: {parsedNumbers.length}
            </p>
          )}
        </div>

        {/* Начальная территория */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Начальная территория слежения
          </label>
          <select
            value={territory}
            onChange={(e) => setTerritory(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100 bg-white"
          >
            <option value="">— не задано —</option>
            {TERRITORIES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <p className="text-xs text-slate-500 mt-1">
            Страна в которой находится вагон/контейнер в текущее время. Используется для биллинга.
          </p>
        </div>

        {/* Снять по окончании маршрута */}
        <label className="flex items-start gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={removeOnRouteEnd}
            onChange={(e) => setRemoveOnRouteEnd(e.target.checked)}
            className="mt-0.5"
          />
          <span className="text-sm">
            <span className="font-medium text-slate-700">Снять по окончании маршрута (рейса)</span>
            <span className="block text-xs text-slate-500 mt-0.5">
              Для гружёных — операции выгрузки на станции назначения,
              для порожних — прибытие на станцию назначения
            </span>
          </span>
        </label>

        {/* Группа */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Группа</label>
          <div className="space-y-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                checked={groupChoice === 'none'}
                onChange={() => setGroupChoice('none')}
              />
              <span className="text-sm text-slate-700">Вне группы</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                checked={groupChoice === 'existing'}
                onChange={() => setGroupChoice('existing')}
                disabled={existingGroups.length === 0}
              />
              <span className="text-sm text-slate-700">Существующая</span>
              <select
                value={existingGroupId}
                onChange={(e) => {
                  setExistingGroupId(e.target.value);
                  setGroupChoice('existing');
                }}
                disabled={existingGroups.length === 0}
                className="flex-1 px-2 py-1 border border-slate-200 rounded text-sm bg-white disabled:bg-slate-50 disabled:text-slate-400"
              >
                {existingGroups.length === 0 ? (
                  <option>— групп нет —</option>
                ) : (
                  existingGroups.map((g) => (
                    <option key={g.id} value={g.id}>{g.name}</option>
                  ))
                )}
              </select>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                checked={groupChoice === 'new'}
                onChange={() => setGroupChoice('new')}
              />
              <span className="text-sm text-slate-700">Новая:</span>
              <input
                type="text"
                value={newGroupName}
                onChange={(e) => {
                  setNewGroupName(e.target.value);
                  setGroupChoice('new');
                }}
                placeholder="Название новой группы"
                className="flex-1 px-2 py-1 border border-slate-200 rounded text-sm"
                maxLength={255}
              />
            </label>
          </div>
        </div>

        {/* Дополнительные параметры */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced((v) => !v)}
            className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-800"
          >
            <Settings2 size={14} />
            Дополнительные параметры
          </button>
          {showAdvanced && (
            <div className="mt-3 space-y-3 pl-2 border-l-2 border-slate-200">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Отложенный старт слежения
                </label>
                <input
                  type="datetime-local"
                  value={deferredStartAt}
                  onChange={(e) => setDeferredStartAt(e.target.value)}
                  className="px-2 py-1 border border-slate-200 rounded text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Автоматическое снятие со слежения
                </label>
                <input
                  type="datetime-local"
                  value={autoRemoveAt}
                  onChange={(e) => setAutoRemoveAt(e.target.value)}
                  className="px-2 py-1 border border-slate-200 rounded text-sm"
                />
              </div>
            </div>
          )}
        </div>

        {err && (
          <p className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{err}</p>
        )}
      </form>
    </Modal>
  );
}
