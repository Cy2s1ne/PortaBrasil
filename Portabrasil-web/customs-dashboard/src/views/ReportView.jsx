import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { API_BASE_URL } from '../shared/config/api';
import { useT } from '../shared/i18n/language-context';
import { buildAuthHeaders, fetchJSON } from '../shared/utils/http';

export default function ReportView({ authToken }) {
  const t = useT();
  const PAGE_SIZE = 10;
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [searchInput, setSearchInput] = useState('');
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  useEffect(() => {
    if (!authToken) return;
    let active = true;
    const offset = (page - 1) * PAGE_SIZE;
    const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(offset) });
    if (query.trim()) params.set('q', query.trim());
    setLoading(true);
    setError('');
    fetchJSON(`${API_BASE_URL}/api/reports/records?${params.toString()}`, {
      headers: buildAuthHeaders(authToken),
    })
      .then((data) => {
        if (!active) return;
        setRows(data?.items || []);
        setTotal(Number(data?.total || 0));
      })
      .catch((err) => {
        if (active) setError(err.message || 'failed');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [authToken, page, query]);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
        <h2 className="text-lg font-bold text-gray-800">{t.recent_records_title}</h2>
        <div className="flex space-x-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  setPage(1);
                  setQuery(searchInput);
                }
              }}
              placeholder={t.search_placeholder}
              className="pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 w-64"
            />
          </div>
          <button
            onClick={() => {
              setPage(1);
              setQuery(searchInput);
            }}
            className="px-4 py-2 border border-gray-200 bg-white rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50"
          >
            {t.filter}
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-gray-500">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 font-semibold">{t.bl_number}</th>
              <th className="px-6 py-4 font-semibold">{t.goods_desc}</th>
              <th className="px-6 py-4 font-semibold">{t.declaration_date}</th>
              <th className="px-6 py-4 font-semibold">{t.port_col}</th>
              <th className="px-6 py-4 font-semibold">{t.status_col}</th>
              <th className="px-6 py-4 font-semibold text-right">{t.action_col}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td className="px-6 py-6 text-sm text-gray-500" colSpan={6}>{t.fetching_rate}</td></tr>
            ) : rows.length === 0 ? (
              <tr><td className="px-6 py-6 text-sm text-gray-400" colSpan={6}>No records.</td></tr>
            ) : rows.map((row) => (
              <tr key={row.id} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-4 font-medium text-gray-900">{row.bl}</td>
                <td className="px-6 py-4">{row.goods_desc || '-'}</td>
                <td className="px-6 py-4">{row.declaration_date || '-'}</td>
                <td className="px-6 py-4">{row.port || '-'}</td>
                <td className="px-6 py-4">
                  {row.status === 'cleared' && <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">{t.status_cleared}</span>}
                  {row.status === 'processing' && <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">{t.status_processing}</span>}
                  {row.status === 'inspection' && <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">{t.status_inspection}</span>}
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">{t.details}</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-6 py-4 border-t border-gray-100 text-sm text-gray-500 flex justify-between items-center">
        <span>{t.total_records(total)}</span>
        <div className="flex space-x-1">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-40"
          >
            {t.prev_page}
          </button>
          <button className="px-3 py-1 bg-blue-50 text-blue-600 border border-blue-200 rounded">{page}</button>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-40"
          >
            {t.next_page}
          </button>
        </div>
      </div>
      {error ? <p className="px-6 pb-4 text-xs text-amber-600">{error}</p> : null}
    </div>
  );
};


