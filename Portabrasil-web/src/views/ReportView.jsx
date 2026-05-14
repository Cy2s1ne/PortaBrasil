import { useCallback, useEffect, useState } from 'react';
import { ArrowLeft, BarChart3, CheckCircle2, ChevronRight, Circle, FileText, Package, Search } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { API_BASE_URL } from '../shared/config/api';
import { useT } from '../shared/i18n/language-context';
import { buildAuthHeaders, fetchJSON } from '../shared/utils/http';
import { formatCurrencyBRL } from '../shared/utils/format';
import { useAuth } from '../shared/auth/useAuth';

const PAGE_SIZE = 10;

export default function ReportView() {
  const { auth } = useAuth();
  const t = useT();
  const authToken = auth?.access_token;
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const urlQuery = searchParams.get('q') || '';
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [searchInput, setSearchInput] = useState(initialQuery);
  const [query, setQuery] = useState(initialQuery);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  useEffect(() => {
    setSearchInput(urlQuery);
    setQuery(urlQuery);
    setPage(1);
    setSelectedDetail(null);
    setDetailError('');
  }, [urlQuery]);

  const applySearch = () => {
    const nextQuery = searchInput.trim();
    setPage(1);
    setQuery(nextQuery);
    setSelectedDetail(null);
    setSearchParams(nextQuery ? { q: nextQuery } : {});
  };

  const loadRows = useCallback(async () => {
    if (!authToken) return;
    const offset = (page - 1) * PAGE_SIZE;
    const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(offset) });
    if (query.trim()) params.set('q', query.trim());
    setLoading(true);
    setError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/reports/records?${params.toString()}`, {
        headers: buildAuthHeaders(authToken),
      });
      setRows(data?.items || []);
      setTotal(Number(data?.total || 0));
    } catch (err) {
      setError(err.message || 'failed');
    } finally {
      setLoading(false);
    }
  }, [authToken, page, query]);

  useEffect(() => {
    loadRows();
  }, [loadRows]);

  const loadDetail = async (recordId) => {
    if (!authToken) return;
    setDetailLoading(true);
    setDetailError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/reports/records/${recordId}`, {
        headers: buildAuthHeaders(authToken),
      });
      setSelectedDetail(data || null);
    } catch (err) {
      setDetailError(err.message || 'failed');
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetail = () => {
    setSelectedDetail(null);
    setDetailError('');
  };

  const renderStatus = (status) => {
    if (status === 'cleared') {
      return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">{t.status_cleared}</span>;
    }
    if (status === 'inspection') {
      return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">{t.status_inspection}</span>;
    }
    return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">{t.status_processing}</span>;
  };

  const renderInfo = (label, value) => (
    <div className="min-w-0">
      <div className="text-xs font-medium text-gray-400 mb-1">{label}</div>
      <div className="text-sm font-semibold text-gray-800 break-words">{value || '-'}</div>
    </div>
  );

  if (selectedDetail || detailLoading) {
    const record = selectedDetail?.record || {};
    const business = selectedDetail?.business || {};
    const steps = selectedDetail?.steps || [];
    const progress = selectedDetail?.progress || { complete_count: 0, total_count: 0, percentage: 0, current_step_no: null };
    const feeItems = selectedDetail?.fee_items || [];
    const feeSummary = selectedDetail?.fee_summary || {};

    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <div className="flex items-center space-x-4">
            <button
              onClick={closeDetail}
              className="inline-flex items-center px-3 py-1.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:text-blue-600 hover:bg-blue-50 hover:border-blue-200 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              {t.back_to_list}
            </button>
            <div>
              <h2 className="text-lg font-bold text-gray-800">{t.report_detail_title}</h2>
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-0.5 text-xs text-gray-400">
                <span>{t.bl_label}<span className="font-semibold text-gray-600">{record.bl || '-'}</span></span>
                <span>{record.goods_desc || '-'}</span>
                <span>{record.port || '-'}</span>
              </div>
            </div>
          </div>
          {record.status ? renderStatus(record.status) : null}
        </div>

        <div className="p-6 space-y-6">
          {detailLoading ? <p className="text-sm text-gray-500">{t.fetching_rate}</p> : null}
          {detailError ? <p className="text-xs text-amber-600">{detailError}</p> : null}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="border border-gray-100 rounded-xl p-5 bg-white">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center text-sm font-bold text-gray-800">
                  <BarChart3 className="w-4 h-4 mr-2 text-blue-500" />
                  {t.report_progress}
                </div>
                <span className="text-sm font-bold text-blue-600">{progress.percentage || 0}%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                <div className="bg-blue-500 h-2.5 rounded-full transition-all" style={{ width: `${progress.percentage || 0}%` }}></div>
              </div>
              <div className="flex justify-between mt-3 text-xs text-gray-500">
                <span>{t.report_completed_steps(progress.complete_count || 0, progress.total_count || 0)}</span>
                <span>{progress.current_step_no ? t[`step${progress.current_step_no}`] : t.all_done}</span>
              </div>
            </div>

            <div className="border border-gray-100 rounded-xl p-5 bg-white">
              <div className="flex items-center text-sm font-bold text-gray-800 mb-4">
                <Package className="w-4 h-4 mr-2 text-emerald-500" />
                {t.report_cargo_summary}
              </div>
              <div className="grid grid-cols-2 gap-4">
                {renderInfo(t.declaration_date, record.declaration_date)}
                {renderInfo(t.report_arrival_date, business.arrival_date)}
                {renderInfo(t.report_destination, business.destination)}
                {renderInfo(t.report_weight, business.gross_weight)}
              </div>
            </div>

            <div className="border border-gray-100 rounded-xl p-5 bg-white">
              <div className="flex items-center text-sm font-bold text-gray-800 mb-4">
                <FileText className="w-4 h-4 mr-2 text-orange-500" />
                {t.report_fee_summary}
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-gray-500">{t.report_total_debit}</span><span className="font-semibold text-gray-800">{formatCurrencyBRL(feeSummary.total_debit)}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">{t.report_total_credit}</span><span className="font-semibold text-gray-800">{formatCurrencyBRL(feeSummary.total_credit)}</span></div>
                <div className="flex justify-between border-t border-gray-100 pt-2"><span className="text-gray-500">{t.report_balance}</span><span className="font-bold text-blue-600">{formatCurrencyBRL(feeSummary.balance)}</span></div>
              </div>
            </div>
          </div>

          <div className="border border-gray-100 rounded-xl p-5">
            <h3 className="text-sm font-bold text-gray-800 mb-4">{t.report_business_info}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
              {renderInfo('S/Ref', business.s_ref)}
              {renderInfo('N/Ref', business.n_ref)}
              {renderInfo(t.report_invoice_no, business.invoice_no)}
              {renderInfo(t.report_customer, business.customer_name)}
              {renderInfo(t.report_mawb_mbl, business.mawb_mbl || record.bl)}
              {renderInfo(t.report_hawb_hbl, business.hawb_hbl)}
              {renderInfo(t.report_cif, business.cif_brl_amount || business.cif_amount)}
              {renderInfo(t.report_data_status, business.data_status)}
            </div>
          </div>

          <div className="border border-gray-100 rounded-xl p-5">
            <h3 className="text-sm font-bold text-gray-800 mb-4">{t.report_process_steps}</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {steps.map((step) => {
                const isComplete = step.status === 'COMPLETE';
                return (
                  <div key={step.id} className={`rounded-lg border p-3 min-h-[104px] ${isComplete ? 'border-green-200 bg-green-50/60' : 'border-gray-200 bg-gray-50/70'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-gray-700">{step.step_no}. {t[`step${step.step_no}`]}</span>
                      {isComplete ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <Circle className="w-4 h-4 text-gray-400" />}
                    </div>
                    <div className={`text-xs font-semibold mb-1 ${isComplete ? 'text-green-600' : 'text-gray-500'}`}>{step.status}</div>
                    <div className="text-xs text-gray-400">{step.date || '-'}</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="border border-gray-100 rounded-xl overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100 flex justify-between items-center">
              <h3 className="text-sm font-bold text-gray-800">{t.report_fee_items}</h3>
              <span className="text-xs text-gray-400">{t.total_records(feeItems.length)}</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-500">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th className="px-5 py-3 font-semibold">{t.report_fee_date}</th>
                    <th className="px-5 py-3 font-semibold">{t.report_fee_code}</th>
                    <th className="px-5 py-3 font-semibold">{t.report_fee_name}</th>
                    <th className="px-5 py-3 font-semibold text-right">{t.report_credit}</th>
                    <th className="px-5 py-3 font-semibold text-right">{t.report_debit}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {feeItems.length === 0 ? (
                    <tr><td className="px-5 py-5 text-sm text-gray-400" colSpan={5}>{t.report_no_fee_items}</td></tr>
                  ) : feeItems.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50/50">
                      <td className="px-5 py-3">{item.fee_date || '-'}</td>
                      <td className="px-5 py-3">{item.fee_code || '-'}</td>
                      <td className="px-5 py-3 font-medium text-gray-800">{item.fee_name || '-'}</td>
                      <td className="px-5 py-3 text-right">{formatCurrencyBRL(item.credit_amount)}</td>
                      <td className="px-5 py-3 text-right">{formatCurrencyBRL(item.debit_amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

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
                  applySearch();
                }
              }}
              placeholder={t.search_placeholder}
              className="pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 w-64"
            />
          </div>
          <button
            onClick={applySearch}
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
                <td className="px-6 py-4">{renderStatus(row.status)}</td>
                <td className="px-6 py-4 text-right">
                  <button
                    onClick={() => loadDetail(row.id)}
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium text-sm"
                  >
                    {t.details} <ChevronRight className="w-4 h-4 ml-0.5" />
                  </button>
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
      {detailError ? <p className="px-6 pb-4 text-xs text-amber-600">{detailError}</p> : null}
    </div>
  );
}
