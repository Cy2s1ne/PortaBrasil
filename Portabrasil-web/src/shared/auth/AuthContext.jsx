import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AUTH_STORAGE_KEY, clearAuthStorage, persistAuth, readStoredAuth } from './storage';
import { API_BASE_URL } from '../config/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => readStoredAuth());
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const authRef = useRef(auth);

  useEffect(() => {
    authRef.current = auth;
  }, [auth]);

  const isLoggedIn = Boolean(auth?.access_token);
  const currentUserName = auth?.user?.real_name || auth?.user?.username || '';
  const currentRoles = auth?.user?.roles || [];
  const canManageAdmins = currentRoles.includes('SUPER_ADMIN') || currentRoles.includes('ADMIN');

  useEffect(() => {
    if (!auth?.access_token) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);

    let active = true;

    fetch(`${API_BASE_URL}/api/auth/me`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${auth.access_token}`,
      },
    })
      .then(async (response) => {
        if (!active) return;
        if (!response.ok) {
          if (response.status === 401 || response.status === 403) {
            clearAuthStorage();
            setAuth(null);
            navigate('/login', { replace: true });
          }
          setIsLoading(false);
          return;
        }
        const data = await response.json();
        if (data?.user) {
          const current = authRef.current;
          const updatedAuth = { ...current, user: data.user };
          setAuth(updatedAuth);
          const remembered = Boolean(localStorage.getItem(AUTH_STORAGE_KEY));
          persistAuth(updatedAuth, remembered);
        }
        setIsLoading(false);
      })
      .catch(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [auth?.access_token, navigate]);

  const login = useCallback((authPayload) => {
    const nextAuth = {
      access_token: authPayload?.access_token || '',
      user: authPayload?.user || null,
    };
    if (!nextAuth.access_token) return;
    const remember = Boolean(authPayload?.remember);
    persistAuth(nextAuth, remember);
    setAuth(nextAuth);
  }, []);

  const logout = useCallback(() => {
    clearAuthStorage();
    setAuth(null);
  }, []);

  const value = {
    auth,
    isLoggedIn,
    isLoading,
    currentUserName,
    currentRoles,
    canManageAdmins,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
