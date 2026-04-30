import { useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './AppLayout';
import LoginPage from './LoginPage';
import { AdminManagementView, CostAnalysisView, HomeView, ProcessTrackingView, ReportView, UploadView } from './views';
import { AuthProvider, useAuth } from './shared/auth/AuthContext';
import RequireAuth from './shared/auth/RequireAuth';

function LoginRoute() {
  const { isLoggedIn } = useAuth();
  if (isLoggedIn) return <Navigate to="/" replace />;
  return <LoginPage />;
}

function AdminRoute({ children }) {
  const { canManageAdmins } = useAuth();
  if (!canManageAdmins) return <Navigate to="/" replace />;
  return children;
}

function AppRoutes({ lang, onLangChange }) {
  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <AppLayout lang={lang} onLangChange={onLangChange} />
          </RequireAuth>
        }
      >
        <Route index element={<HomeView />} />
        <Route path="upload" element={<UploadView />} />
        <Route path="process" element={<ProcessTrackingView />} />
        <Route path="cost" element={<CostAnalysisView />} />
        <Route path="report" element={<ReportView />} />
        <Route path="admin" element={<AdminRoute><AdminManagementView /></AdminRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  const [lang, setLang] = useState('zh');

  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes lang={lang} onLangChange={setLang} />
      </AuthProvider>
    </BrowserRouter>
  );
}
