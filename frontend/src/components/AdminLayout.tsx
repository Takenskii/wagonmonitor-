/** Common shell: sidebar with role-aware nav + outlet for the page content. */
import { NavLink, Outlet } from 'react-router-dom';

import { useAuth } from '../auth/useAuth';

const navClass = ({ isActive }: { isActive: boolean }) =>
  `block px-3 py-2 rounded-lg text-sm transition-colors ${
    isActive
      ? 'bg-blue-600 text-white'
      : 'text-slate-400 hover:bg-slate-800 hover:text-white'
  }`;

export default function AdminLayout() {
  const { user, logout } = useAuth();
  if (!user) return null;

  const isSuperadmin = user.role === 'superadmin';
  const isAdmin = isSuperadmin || user.role === 'admin';

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50">
      <aside className="w-56 bg-slate-900 text-slate-300 flex flex-col shrink-0">
        <div className="h-14 flex items-center px-4 border-b border-slate-800">
          <span className="text-white font-bold">Wagon Monitor</span>
        </div>

        <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
          <NavLink to="/" end className={navClass}>
            Главная
          </NavLink>
          {isSuperadmin && (
            <NavLink to="/admin/companies" className={navClass}>
              Компании
            </NavLink>
          )}
          {isAdmin && (
            <NavLink to="/admin/users" className={navClass}>
              Пользователи
            </NavLink>
          )}
        </nav>

        <div className="p-3 border-t border-slate-800 text-xs">
          <div className="text-slate-400 mb-1 truncate" title={user.email}>
            {user.email}
          </div>
          <div className="text-slate-500 mb-3">{user.role}</div>
          <button
            onClick={logout}
            className="w-full text-left text-rose-400 hover:text-rose-300"
          >
            Выйти
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
