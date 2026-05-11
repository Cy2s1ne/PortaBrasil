import { useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './AppLayout';
import LoginPage from './LoginPage';
import { AdminManagementView, AuditReviewView, CostAnalysisView, HomeView, ProcessTrackingView, ReportView, UploadView } from './views';
import { AuthProvider, useAuth } from './shared/auth/AuthContext';
import RequireAuth from './shared/auth/RequireAuth';

function LoginRoute({ lang, onLangChange }) {
  const { isLoggedIn } = useAuth();
  if (isLoggedIn) return <Navigate to="/" replace />;
  return <LoginPage lang={lang} onLangChange={onLangChange} />;
}

function AdminRoute({ children }) {
  const { canManageAdmins } = useAuth();
  if (!canManageAdmins) return <Navigate to="/" replace />;
  return children;
}

function RoleRoute({ canAccess, children }) {
  if (!canAccess) return <Navigate to="/" replace />;
  return children;
}

function AppRoutes({ lang, onLangChange }) {
  const { canAccessUpload, canAccessCost, canAccessAudit, canAccessReport } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginRoute lang={lang} onLangChange={onLangChange} />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <AppLayout lang={lang} onLangChange={onLangChange} />
          </RequireAuth>
        }
      >
        <Route index element={<HomeView />} />
        <Route path="upload" element={<RoleRoute canAccess={canAccessUpload}><UploadView /></RoleRoute>} />
        <Route path="process" element={<ProcessTrackingView />} />
        <Route path="cost" element={<RoleRoute canAccess={canAccessCost}><CostAnalysisView /></RoleRoute>} />
        <Route path="audit" element={<RoleRoute canAccess={canAccessAudit}><AuditReviewView /></RoleRoute>} />
        <Route path="report" element={<RoleRoute canAccess={canAccessReport}><ReportView /></RoleRoute>} />
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
