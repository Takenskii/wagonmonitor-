import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { AuthProvider } from './auth/useAuth';
import { RequireAuth } from './routes/RequireAuth';
import AdminLayout from './components/AdminLayout';
import LoginPage from './pages/Login';
import DislocationPage from './pages/Dislocation';
import CompaniesPage from './pages/Companies';
import UsersPage from './pages/Users';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<RequireAuth />}>
              <Route element={<AdminLayout />}>
                <Route path="/" element={<Navigate to="/dislocations" replace />} />
                <Route path="/dislocations" element={<DislocationPage />} />
                <Route path="/admin/companies" element={<CompaniesPage />} />
                <Route path="/admin/users" element={<UsersPage />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/dislocations" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
