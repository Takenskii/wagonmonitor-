/** Teal sidebar + masquerade banner. Inspired by wagonmonitor.kz. */
import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  MapPin,
  Train,
  Mail,
  ScrollText,
  KeyRound,
  Users,
  Building2,
  ChevronLeft,
  ChevronRight,
  LogOut,
  AlertTriangle,
} from 'lucide-react';

import { useAuth } from '../auth/useAuth';

interface NavItem {
  to: string;
  label: string;
  icon: typeof MapPin;
  roles: Array<'superadmin' | 'admin' | 'user'>;
}

const NAV: NavItem[] = [
  { to: '/dislocations', label: 'Слежение', icon: MapPin, roles: ['superadmin', 'admin', 'user'] },
  { to: '/groups', label: 'Группы вагонов', icon: Train, roles: ['superadmin', 'admin', 'user'] },
  { to: '/reports', label: 'Почтовые рассылки', icon: Mail, roles: ['superadmin', 'admin', 'user'] },
  { to: '/audit', label: 'Журнал операций', icon: ScrollText, roles: ['superadmin', 'admin'] },
  { to: '/api', label: 'API', icon: KeyRound, roles: ['superadmin'] },
  { to: '/admin/users', label: 'Пользователи', icon: Users, roles: ['superadmin', 'admin'] },
  { to: '/admin/companies', label: 'Компании', icon: Building2, roles: ['superadmin'] },
];

export default function AdminLayout() {
  const { user, logout, isImpersonating, originalUser, exitImpersonation } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  if (!user) return null;

  const items = NAV.filter((i) => i.roles.includes(user.role));

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50">
      {/* ── Sidebar ─────────────────────────────────────────────────── */}
      <aside
        className={`${collapsed ? 'w-16' : 'w-56'} bg-[#4A9EA0] text-white flex flex-col shrink-0 transition-all duration-200`}
      >
        <div className="h-12 flex items-center justify-between px-4 border-b border-white/15 shrink-0">
          {!collapsed && <span className="font-semibold tracking-wide">Система</span>}
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="text-white/80 hover:text-white"
            aria-label={collapsed ? 'Развернуть' : 'Свернуть'}
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto py-2">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/dislocations'}
              className={({ isActive }) =>
                `flex items-center justify-between gap-2 px-4 py-2.5 text-sm transition-colors ${
                  isActive
                    ? 'bg-[#3D8587] text-white'
                    : 'text-white/90 hover:bg-[#3D8587]/70'
                } ${collapsed ? 'justify-center px-0' : ''}`
              }
              title={collapsed ? label : undefined}
            >
              {!collapsed && <span className="truncate">{label}</span>}
              <Icon size={16} className={collapsed ? '' : 'shrink-0'} />
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/15 p-3 text-xs">
          {!collapsed ? (
            <>
              <div className="truncate" title={user.email}>{user.email}</div>
              <div className="text-white/70 mb-2">{user.role}</div>
              <button
                onClick={logout}
                className="inline-flex items-center gap-1.5 text-rose-200 hover:text-white"
              >
                <LogOut size={13} />
                Выйти
              </button>
            </>
          ) : (
            <button
              onClick={logout}
              className="block w-full text-rose-200 hover:text-white"
              title="Выйти"
            >
              <LogOut size={16} className="mx-auto" />
            </button>
          )}
        </div>
      </aside>

      {/* ── Main ────────────────────────────────────────────────────── */}
      <main className="flex-1 overflow-auto flex flex-col">
        {isImpersonating && originalUser && (
          <div className="bg-rose-50 border-b border-rose-200 text-rose-700 px-4 py-2 flex items-center gap-3">
            <AlertTriangle size={16} className="shrink-0" />
            <span className="text-sm flex-1">
              Вы вошли как <strong>{user.email}</strong> (от имени <strong>{originalUser.email}</strong>)
            </span>
            <button
              onClick={exitImpersonation}
              className="text-sm font-medium px-3 py-1 bg-rose-600 text-white rounded-lg hover:bg-rose-700"
            >
              Вернуться
            </button>
          </div>
        )}
        <div className="flex-1">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
