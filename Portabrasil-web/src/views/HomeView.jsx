import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, ChevronRight, Clock, DollarSign, FileCheck } from 'lucide-react';
import { API_BASE_URL } from '../shared/config/api';
import { useT } from '../shared/i18n/language-context';
import { formatCurrencyBRL } from '../shared/utils/format';
import { buildAuthHeaders, fetchJSON } from '../shared/utils/http';
import { useAuth } from '../shared/auth/AuthContext';

export default function HomeView() {
  const { auth } = useAuth();
  const t = useT();
  const authToken = auth?.access_token;
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authToken) return;
    let active = true;
    fetchJSON(`${API_BASE_URL}/api/dashboard/overview`, {
      headers: buildAuthHeaders(authToken),
    })
      .then((data) => {
        if (active) {
          setOverview(data || null);
          setError('');
        }
      })
      .catch((err) => {
        if (active) setError(err.message || 'failed');
      });
    return () => {
      active = false;
    };
  }, [authToken]);

  const stats = overview?.stats || {
    in_progress: 0,
    taxes_due: 0,
    anomaly: 0,
    done_month: 0,
  };
  const kanban = overview?.kanban || { items: [], total: 0, normal: 0, anomaly: 0 };
  const stepCountMap = new Map((kanban.items || []).map((item) => [Number(item.step_no), Number(item.count || 0)]));
  const activities = (overview?.activities || []).slice(0, 10);

  const cols = [
    { id: 1, titleKey: 'step1', color: { topBar: 'bg-violet-500', card: 'bg-gradient-to-b from-violet-50 to-white border-violet-300', label: 'text-violet-600', count: 'text-violet-600', unit: 'text-violet-500' } },
    { id: 2, titleKey: 'step2', color: { topBar: 'bg-blue-500', card: 'bg-gradient-to-b from-blue-50 to-white border-blue-300', label: 'text-blue-600', count: 'text-blue-600', unit: 'text-blue-500' } },
    { id: 3, titleKey: 'step3', color: { topBar: 'bg-cyan-500', card: 'bg-gradient-to-b from-cyan-50 to-white border-cyan-300', label: 'text-cyan-600', count: 'text-cyan-600', unit: 'text-cyan-500' } },
    { id: 4, titleKey: 'step4', color: { topBar: 'bg-teal-500', card: 'bg-gradient-to-b from-teal-50 to-white border-teal-300', label: 'text-teal-600', count: 'text-teal-600', unit: 'text-teal-500' } },
    { id: 5, titleKey: 'step5', color: { topBar: 'bg-green-500', card: 'bg-gradient-to-b from-green-50 to-white border-green-300', label: 'text-green-600', count: 'text-green-600', unit: 'text-green-500' } },
    { id: 6, titleKey: 'step6', color: { topBar: 'bg-red-500', card: 'bg-gradient-to-b from-red-50 to-white border-red-300', label: 'text-red-600', count: 'text-red-600', unit: 'text-red-500' } },
    { id: 7, titleKey: 'step7', color: { topBar: 'bg-amber-500', card: 'bg-gradient-to-b from-amber-50 to-white border-amber-300', label: 'text-amber-600', count: 'text-amber-600', unit: 'text-amber-500' } },
    { id: 8, titleKey: 'step8', color: { topBar: 'bg-orange-500', card: 'bg-gradient-to-b from-orange-50 to-white border-orange-300', label: 'text-orange-600', count: 'text-orange-600', unit: 'text-orange-500' } },
    { id: 9, titleKey: 'step9', color: { topBar: 'bg-pink-500', card: 'bg-gradient-to-b from-pink-50 to-white border-pink-300', label: 'text-pink-600', count: 'text-pink-600', unit: 'text-pink-500' } },
    { id: 10, titleKey: 'step10', color: { topBar: 'bg-indigo-500', card: 'bg-gradient-to-b from-indigo-50 to-white border-indigo-300', label: 'text-indigo-600', count: 'text-indigo-600', unit: 'text-indigo-500' } },
  ];

  const renderRow = (items) => (
    <div className="grid grid-cols-5 gap-3">
      {items.map((col) => {
        const c = col.color;
        const count = stepCountMap.get(col.id) || 0;
        return (
          <div key={col.id} className={`flex flex-col rounded-xl border-2 overflow-hidden shadow-sm hover:shadow-lg transition-all duration-200 hover:-translate-y-0.5 ${c.card}`}>
            <div className={`h-1.5 w-full ${c.topBar}`}></div>
            <div className="px-4 py-4 flex flex-col items-center text-center">
              <span className={`text-xs font-bold uppercase tracking-widest mb-2 ${c.label}`}>STEP {col.id}</span>
              <div className={`text-5xl font-black leading-none mb-1 ${c.count}`}>{count}</div>
              <div className={`text-xs font-semibold mb-3 ${c.unit}`}>{t.kanban_unit}</div>
              <div className="text-sm font-bold text-gray-700 leading-snug">{t[col.titleKey]}</div>
            </div>
          </div>
        );
      })}
    </div>
  );

  const statCards = [
    { titleKey: 'stat_inProgress', value: stats.in_progress || 0, icon: Clock, color: 'text-blue-500', bg: 'bg-blue-50' },
    { titleKey: 'stat_taxes', value: formatCurrencyBRL(stats.taxes_due), icon: DollarSign, color: 'text-orange-500', bg: 'bg-orange-50' },
    { titleKey: 'stat_anomaly', value: stats.anomaly || 0, icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-50' },
    { titleKey: 'stat_done', value: stats.done_month || 0, icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-50' },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">{t.welcome}</h2>
          <p className="text-gray-500">{t.welcomeSub(stats.in_progress || 0, stats.anomaly || 0)}</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm">
          {t.newDeclaration}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {statCards.map((stat, i) => (
          <div key={i} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center space-x-4">
            <div className={`p-4 rounded-xl ${stat.bg}`}>
              <stat.icon className={`w-7 h-7 ${stat.color}`} />
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">{t[stat.titleKey]}</div>
              <div className="text-2xl font-bold text-gray-800">{stat.value}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="mb-5">
          <h3 className="text-lg font-bold text-gray-800">{t.kanban_title}</h3>
          <p className="text-xs text-gray-400 mt-0.5">{t.kanban_desc}</p>
        </div>
        <div className="space-y-3">
          {renderRow(cols.slice(0, 5))}
          {renderRow(cols.slice(5, 10))}
        </div>
        <div className="mt-5 pt-4 border-t border-gray-100 flex items-center justify-between text-sm">
          <div className="flex space-x-6">
            <span className="text-gray-500">{t.kanban_total}<span className="font-bold text-gray-800">{kanban.total || 0}</span> {t.kanban_unit}</span>
            <span className="text-gray-500">{t.kanban_normal}<span className="font-bold text-gray-800">{kanban.normal || 0}</span></span>
            <span className="text-red-500 font-medium">{t.kanban_anomaly_label}<span className="font-bold">{kanban.anomaly || 0}</span></span>
          </div>
          <button className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center">
            {t.kanban_viewAll} <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
          </button>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-6 px-2">{t.activity_title}</h3>
        <div className="space-y-0 relative before:absolute before:inset-0 before:ml-6 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-200 before:to-transparent">
          {(activities.length ? activities : [
            { type: 'ALERT', title: t.act1_title, description: t.act1_desc, time: t.act1_time },
            { type: 'SUCCESS', title: t.act2_title, description: t.act2_desc, time: t.act2_time },
            { type: 'INFO', title: t.act3_title, description: t.act3_desc, time: t.act3_time },
          ]).map((item, i) => (
            <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-blue-100 text-blue-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                {String(item.type || '').toUpperCase() === 'ALERT' ? <AlertTriangle className="w-4 h-4 text-red-500" /> :
                  String(item.type || '').toUpperCase() === 'SUCCESS' ? <CheckCircle2 className="w-4 h-4 text-green-500" /> :
                    <FileCheck className="w-4 h-4 text-blue-500" />}
              </div>
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-gray-100 bg-gray-50/50 shadow-sm">
                <div className="flex items-center justify-between space-x-2 mb-1">
                  <div className="font-bold text-gray-800">{item.title}</div>
                  <div className="text-xs font-medium text-gray-500">{item.time || ''}</div>
                </div>
                <div className="text-sm text-gray-600">{item.description}</div>
              </div>
            </div>
          ))}
        </div>
        {error ? <p className="mt-4 text-xs text-amber-600">{error}</p> : null}
      </div>
    </div>
  );
}
