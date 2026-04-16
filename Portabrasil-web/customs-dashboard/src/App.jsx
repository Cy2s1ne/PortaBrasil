import { useEffect, useState } from 'react';
import {
  BarChart2,
  Bell,
  ChevronRight,
  Globe,
  Home,
  Layers,
  LogOut,
  Map as MapIcon,
  PieChart,
  Search,
  UploadCloud,
} from 'lucide-react';
import LoginPage from './LoginPage';
import SidebarItem from './components/navigation/SidebarItem';
import { AUTH_STORAGE_KEY, clearAuthStorage, persistAuth, readStoredAuth } from './shared/auth/storage';
import { API_BASE_URL } from './shared/config/api';
import { LanguageContext } from './shared/i18n/language-context';
import { TRANSLATIONS } from './shared/i18n/translations';
import { CostAnalysisView, HomeView, ProcessTrackingView, ReportView, UploadView } from './views';

const LANGS = ['zh', 'en', 'pt'];
const LANG_LABELS = { zh: '中文', en: 'EN', pt: 'PT' };

export default function App() {
  const [activeMenu, setActiveMenu] = useState('home');
  const [lang, setLang] = useState('zh');
  const [auth, setAuth] = useState(() => readStoredAuth());

  const t = TRANSLATIONS[lang] || TRANSLATIONS.zh;
  const isLoggedIn = Boolean(auth?.access_token);
  const currentUserName = auth?.user?.real_name || auth?.user?.username || t.admin;

  useEffect(() => {
    if (!auth?.access_token) return;
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
          }
          return;
        }
        const data = await response.json();
        if (data?.user) {
          const updatedAuth = { ...auth, user: data.user };
          setAuth(updatedAuth);
          const remembered = Boolean(localStorage.getItem(AUTH_STORAGE_KEY));
          persistAuth(updatedAuth, remembered);
        }
      })
      .catch(() => {});

    return () => {
      active = false;
    };
  }, [auth?.access_token]);

  const handleLogin = (authPayload) => {
    const nextAuth = {
      access_token: authPayload?.access_token || '',
      user: authPayload?.user || null,
    };
    if (!nextAuth.access_token) return;
    const remember = Boolean(authPayload?.remember);
    persistAuth(nextAuth, remember);
    setAuth(nextAuth);
  };

  const handleLogout = () => {
    clearAuthStorage();
    setAuth(null);
  };

  const menuItems = [
    { key: 'home', label: t.nav_home, icon: Home },
    { key: 'upload', label: t.nav_upload, icon: UploadCloud },
    { key: 'process', label: t.nav_process, icon: MapIcon },
    { key: 'cost', label: t.nav_cost, icon: PieChart },
    { key: 'report', label: t.nav_report, icon: BarChart2 },
  ];

  const renderContent = () => {
    switch (activeMenu) {
      case 'home':
        return <HomeView authToken={auth?.access_token} />;
      case 'upload':
        return <UploadView authToken={auth?.access_token} />;
      case 'process':
        return <ProcessTrackingView authToken={auth?.access_token} />;
      case 'cost':
        return <CostAnalysisView authToken={auth?.access_token} />;
      case 'report':
        return <ReportView authToken={auth?.access_token} />;
      default:
        return <HomeView authToken={auth?.access_token} />;
    }
  };

  const activeLabel = menuItems.find((menuItem) => menuItem.key === activeMenu)?.label || '';

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} lang={lang} onLangChange={setLang} />;
  }

  return (
    <LanguageContext.Provider value={lang}>
      <div className="flex h-screen bg-[#f4f7f9] font-sans">
        <div className="w-64 bg-white border-r border-gray-200 flex flex-col shadow-sm z-10 shrink-0">
          <div className="h-16 flex items-center px-6 border-b border-gray-100">
            <div className="flex items-center text-blue-600">
              <Layers className="w-7 h-7 mr-2 fill-current text-blue-500" />
              <span className="font-bold text-lg tracking-tight text-gray-900">{t.appName}</span>
            </div>
          </div>
          <div className="flex-1 py-6 overflow-y-auto">
            {menuItems.map((item) => (
              <SidebarItem
                key={item.key}
                icon={item.icon}
                label={item.label}
                isActive={activeMenu === item.key}
                onClick={() => setActiveMenu(item.key)}
              />
            ))}
          </div>

          <div className="p-4 border-t border-gray-100">
            <div className="bg-blue-50 rounded-xl p-4 flex flex-col items-center text-center">
              <div className="bg-white p-2 rounded-full shadow-sm mb-2 text-blue-500">
                <MapIcon className="w-5 h-5" />
              </div>
              <div className="text-sm font-semibold text-gray-800 mb-1">{t.needHelp}</div>
              <div className="text-xs text-gray-500 mb-3">{t.helpDesc}</div>
              <button className="text-xs bg-blue-600 text-white px-4 py-1.5 rounded-lg w-full hover:bg-blue-700 transition-colors">
                {t.contactSupport}
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8 shadow-sm z-0 shrink-0">
            <div className="flex items-center text-gray-500 text-sm">
              <span className="hover:text-gray-800 cursor-pointer">{t.system}</span>
              <ChevronRight className="w-4 h-4 mx-2" />
              <span className="font-medium text-gray-800">{activeLabel}</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative hidden md:block">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder={t.globalSearch}
                  className="pl-9 pr-4 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-100 w-48 transition-all focus:w-64"
                />
              </div>

              <button
                onClick={() => setLang((currentLang) => {
                  const currentIndex = LANGS.indexOf(currentLang);
                  return LANGS[(currentIndex + 1) % 3];
                })}
                className="flex items-center space-x-1 text-gray-500 hover:text-blue-600 px-2.5 py-1 rounded-lg hover:bg-blue-50 transition-colors border border-gray-200"
              >
                <Globe className="w-4 h-4" />
                <span className="text-xs font-semibold">{LANG_LABELS[lang]}</span>
              </button>

              <button className="text-gray-400 hover:text-gray-600 transition-colors relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
              </button>

              <button
                onClick={handleLogout}
                className="flex items-center space-x-1 text-gray-400 hover:text-red-500 px-2.5 py-1 rounded-lg hover:bg-red-50 transition-colors border border-gray-200"
              >
                <LogOut className="w-4 h-4" />
              </button>

              <div className="h-8 w-px bg-gray-200"></div>
              <div className="flex items-center cursor-pointer hover:bg-gray-50 p-1.5 rounded-lg transition-colors">
                <img
                  src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix&backgroundColor=e2e8f0"
                  alt="User Avatar"
                  className="w-8 h-8 rounded-full bg-gray-100 border border-gray-200 mr-2"
                />
                <span className="font-medium text-sm text-gray-700">{currentUserName}</span>
              </div>
            </div>
          </header>

          <main className="flex-1 overflow-auto p-8">
            <div className="max-w-[1400px] mx-auto">{renderContent()}</div>
          </main>
        </div>
      </div>
    </LanguageContext.Provider>
  );
}
