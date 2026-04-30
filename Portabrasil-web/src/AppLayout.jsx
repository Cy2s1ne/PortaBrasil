import { NavLink, Outlet, useLocation } from 'react-router-dom';
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
  ShieldCheck,
  UploadCloud,
} from 'lucide-react';
import SidebarItem from './components/navigation/SidebarItem';
import { useAuth } from './shared/auth/AuthContext';
import { LanguageContext } from './shared/i18n/language-context';
import { TRANSLATIONS } from './shared/i18n/translations';

const LANGS = ['zh', 'en', 'pt'];
const LANG_LABELS = { zh: '中文', en: 'EN', pt: 'PT' };

export default function AppLayout({ lang, onLangChange }) {
  const { currentUserName, canManageAdmins, logout } = useAuth();
  const location = useLocation();
  const t = TRANSLATIONS[lang] || TRANSLATIONS.zh;

  const menuItems = [
    { key: 'home', label: t.nav_home, icon: Home, path: '/' },
    { key: 'upload', label: t.nav_upload, icon: UploadCloud, path: '/upload' },
    { key: 'process', label: t.nav_process, icon: MapIcon, path: '/process' },
    { key: 'cost', label: t.nav_cost, icon: PieChart, path: '/cost' },
    { key: 'report', label: t.nav_report, icon: BarChart2, path: '/report' },
    ...(canManageAdmins ? [{ key: 'admin', label: t.nav_admin, icon: ShieldCheck, path: '/admin' }] : []),
  ];

  const routeLabels = {
    '/': t.nav_home,
    '/upload': t.nav_upload,
    '/process': t.nav_process,
    '/cost': t.nav_cost,
    '/report': t.nav_report,
    '/admin': t.nav_admin,
  };

  const activeLabel = routeLabels[location.pathname] || '';

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
                to={item.path}
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
                onClick={() => onLangChange((currentLang) => {
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
                onClick={logout}
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
            <div className="max-w-[1400px] mx-auto">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </LanguageContext.Provider>
  );
}
