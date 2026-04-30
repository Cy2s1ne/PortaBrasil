import React, { useEffect, useState } from 'react';
import { ArrowRight, CheckCircle2, ChevronRight, Circle, Download, Edit2, Search, X } from 'lucide-react';
import { API_BASE_URL } from '../shared/config/api';
import { useT } from '../shared/i18n/language-context';
import { buildAuthHeaders, fetchJSON } from '../shared/utils/http';
import { useAuth } from '../shared/auth/AuthContext';

export default function ProcessTrackingView() {
  const { auth } = useAuth();
  const t = useT();
  const authToken = auth?.access_token;
  const PAGE_SIZE = 10;
  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [searchInput, setSearchInput] = useState('');
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [listLoading, setListLoading] = useState(false);
  const [listError, setListError] = useState('');

  const [selectedRecord, setSelectedRecord] = useState(null);
  const [stepsData, setStepsData] = useState([]);
  const [progress, setProgress] = useState({ complete_count: 0, total_count: 10, percentage: 0, current_step_no: null });
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');

  const [editingStep, setEditingStep] = useState(null);
  const [editForm, setEditForm] = useState({ status: '', date: '', desc: '' });
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saving, setSaving] = useState(false);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const loadList = async () => {
    if (!authToken) return;
    setListLoading(true);
    setListError('');
    const offset = (page - 1) * PAGE_SIZE;
    const params = new URLSearchParams({
      limit: String(PAGE_SIZE),
      offset: String(offset),
    });
    if (query.trim()) params.set('q', query.trim());
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/process/records?${params.toString()}`, {
        headers: buildAuthHeaders(authToken),
      });
      setRecords(data?.items || []);
      setTotal(Number(data?.total || 0));
    } catch (err) {
      setListError(err.message || 'failed');
    } finally {
      setListLoading(false);
    }
  };

  useEffect(() => {
    loadList();
  }, [authToken, page, query]);

  const loadDetail = async (recordId) => {
    if (!authToken) return;
    setDetailLoading(true);
    setDetailError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/process/records/${recordId}`, {
        headers: buildAuthHeaders(authToken),
      });
      setSelectedRecord(data?.record || null);
      setStepsData((data?.steps || []).map((step) => ({
        id: Number(step.step_no),
        status: step.status || 'PENDING',
        date: step.date || '',
        desc: step.desc || '',
      })));
      setProgress(data?.progress || { complete_count: 0, total_count: 10, percentage: 0, current_step_no: null });
    } catch (err) {
      setDetailError(err.message || 'failed');
    } finally {
      setDetailLoading(false);
    }
  };

  const openEdit = (step) => {
    setEditingStep(step);
    setEditForm({ status: step.status, date: step.date || '', desc: step.desc || t[`step${step.id}_desc`] });
    setSaveSuccess(false);
  };

  const closeEdit = () => {
    setEditingStep(null);
    setSaveSuccess(false);
  };

  const saveEdit = async () => {
    if (!selectedRecord || !editingStep || !authToken || saving) return;
    setSaving(true);
    setDetailError('');
    try {
      const data = await fetchJSON(
        `${API_BASE_URL}/api/process/records/${selectedRecord.id}/steps/${editingStep.id}`,
        {
          method: 'PUT',
          headers: buildAuthHeaders(authToken, { 'Content-Type': 'application/json' }),
          body: JSON.stringify({
            status: editForm.status,
            date: editForm.date,
            desc: editForm.desc,
          }),
        }
      );
      setSelectedRecord(data?.record || selectedRecord);
      setStepsData((data?.steps || []).map((step) => ({
        id: Number(step.step_no),
        status: step.status || 'PENDING',
        date: step.date || '',
        desc: step.desc || '',
      })));
      setProgress(data?.progress || progress);
      setSaveSuccess(true);
      setTimeout(() => closeEdit(), 900);
      loadList();
    } catch (err) {
      setDetailError(err.message || 'failed');
    } finally {
      setSaving(false);
    }
  };

  const completedCount = Number(progress?.complete_count ?? stepsData.filter((s) => s.status === 'COMPLETE').length);
  const totalCount = Number(progress?.total_count || stepsData.length || 10);
  const progressPercentage = Number(progress?.percentage ?? (totalCount ? Math.round((completedCount / totalCount) * 100) : 0));
  const currentStepNo = progress?.current_step_no || (stepsData.find((s) => s.status !== 'COMPLETE')?.id ?? null);

  const renderStepCard = (step, index, rowLength) => {
    const isComplete = step.status === 'COMPLETE';
    return (
      <React.Fragment key={step.id}>
        <div className={`relative flex flex-col items-center p-5 rounded-xl border-2 w-[200px] h-[200px] text-center shrink-0 transition-all duration-300 hover:shadow-md ${
          isComplete ? 'border-green-400 bg-[#f0fcf4]' : 'border-red-400 bg-white'
        }`}>
          <button
            onClick={() => openEdit(step)}
            className="absolute top-2 right-2 p-1 rounded-md text-gray-300 hover:text-blue-500 hover:bg-blue-50 transition-colors"
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>
          <div className="mb-3 mt-1">
            {isComplete ? <CheckCircle2 className="w-9 h-9 text-green-500" /> : <Circle className="w-9 h-9 text-red-500" strokeWidth={1.5} />}
          </div>
          <h3 className="font-semibold text-gray-800 mb-1 text-[15px] leading-tight">{step.id}. {t[`step${step.id}`]}</h3>
          <div className={`font-bold text-sm mb-1 tracking-wide ${isComplete ? 'text-green-600' : 'text-[#c62828]'}`}>{step.status}</div>
          <div className="text-xs text-gray-500 font-medium h-[16px] mb-1">{step.date}</div>
          <div className="text-xs text-gray-500 leading-relaxed mt-auto overflow-hidden line-clamp-3">{step.desc || t[`step${step.id}_desc`]}</div>
        </div>
        {index < rowLength - 1 && (
          <div className="flex-1 flex justify-center text-indigo-300">
            <ArrowRight className="w-8 h-8 opacity-60" strokeWidth={1.5} />
          </div>
        )}
      </React.Fragment>
    );
  };

  if (!selectedRecord) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <div>
            <h2 className="text-lg font-bold text-gray-800">{t.process_list_title}</h2>
            <p className="text-xs text-gray-400 mt-0.5">{t.process_list_desc}</p>
          </div>
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
              {listLoading ? (
                <tr><td className="px-6 py-6 text-sm text-gray-500" colSpan={6}>{t.fetching_rate}</td></tr>
              ) : records.length === 0 ? (
                <tr><td className="px-6 py-6 text-sm text-gray-400" colSpan={6}>No records.</td></tr>
              ) : records.map((row) => (
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
                    <button
                      onClick={() => loadDetail(row.id)}
                      className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium text-sm"
                    >
                      {t.view_process} <ChevronRight className="w-4 h-4 ml-0.5" />
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
        {listError ? <p className="px-6 pb-4 text-xs text-amber-600">{listError}</p> : null}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 overflow-hidden min-w-[1100px]">
      {editingStep && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl w-[440px] p-7 relative">
            {saveSuccess && (
              <div className="absolute inset-0 bg-white/90 rounded-2xl flex flex-col items-center justify-center z-10">
                <CheckCircle2 className="w-12 h-12 text-green-500 mb-3" />
                <span className="text-lg font-semibold text-green-600">{t.save_success}</span>
              </div>
            )}
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-gray-800">{t.edit_step_title}</h3>
              <button onClick={closeEdit} className="text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">{t.step_name_label}</label>
                <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-600 font-medium">
                  {editingStep.id}. {t[`step${editingStep.id}`]}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">{t.status_label}</label>
                <div className="flex space-x-3">
                  <button
                    onClick={() => setEditForm((prev) => ({ ...prev, status: 'COMPLETE' }))}
                    className={`flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-lg border-2 text-sm font-semibold transition-all ${
                      editForm.status === 'COMPLETE' ? 'border-green-400 bg-green-50 text-green-700' : 'border-gray-200 text-gray-500 hover:border-green-300 hover:bg-green-50/50'
                    }`}
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>COMPLETE</span>
                  </button>
                  <button
                    onClick={() => setEditForm((prev) => ({ ...prev, status: 'PENDING' }))}
                    className={`flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-lg border-2 text-sm font-semibold transition-all ${
                      editForm.status === 'PENDING' ? 'border-red-400 bg-red-50 text-red-700' : 'border-gray-200 text-gray-500 hover:border-red-300 hover:bg-red-50/50'
                    }`}
                  >
                    <Circle className="w-4 h-4" strokeWidth={2} />
                    <span>PENDING</span>
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  {t.completion_time_label} <span className="text-gray-400 font-normal">{t.completion_time_hint}</span>
                </label>
                <input
                  type="text"
                  placeholder={t.completion_time_ph}
                  value={editForm.date}
                  onChange={(e) => setEditForm((prev) => ({ ...prev, date: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">{t.step_desc_label}</label>
                <textarea
                  rows={3}
                  value={editForm.desc}
                  onChange={(e) => setEditForm((prev) => ({ ...prev, desc: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 resize-none"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={closeEdit}
                className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
              >
                {t.cancel}
              </button>
              <button
                onClick={saveEdit}
                disabled={saving}
                className="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-60"
              >
                {saving ? t.fetching_rate : t.save_update}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="px-8 py-6 border-b border-gray-100 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => {
              setSelectedRecord(null);
              setEditingStep(null);
            }}
            className="flex items-center text-sm text-gray-500 hover:text-blue-600 font-medium px-3 py-1.5 rounded-lg hover:bg-blue-50 border border-gray-200 hover:border-blue-200 transition-colors"
          >
            <ArrowRight className="w-4 h-4 mr-1.5 rotate-180" /> {t.back_to_list}
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-800">{t.container_title}</h1>
            <div className="flex items-center space-x-3 mt-0.5 text-xs text-gray-400">
              <span>{t.bl_label}<span className="font-semibold text-gray-600">{selectedRecord.bl}</span></span>
              <span>·</span>
              <span>{selectedRecord.goods_desc || '-'}</span>
              <span>·</span>
              <span>{selectedRecord.port || '-'}</span>
            </div>
          </div>
        </div>
        <div className="flex space-x-3">
          <button className="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 flex items-center">
            <Download className="w-4 h-4 mr-2" /> {t.export_progress}
          </button>
        </div>
      </div>

      <div className="p-8">
        <div className="bg-gray-50 rounded-xl p-6 mb-10 border border-gray-100">
          <div className="flex flex-col space-y-4">
            <div className="flex items-center text-sm">
              <span className="text-gray-500 w-32">{t.overall_progress}</span>
              <span className="font-medium text-gray-800">{completedCount}/{totalCount} ({progressPercentage}%)</span>
            </div>
            <div className="flex items-center text-sm">
              <span className="text-gray-500 w-32">{t.current_step_label}</span>
              <span className="font-medium text-gray-800">{currentStepNo ? t[`step${currentStepNo}`] : t.all_done}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3.5 mt-2 overflow-hidden border border-gray-200/50">
              <div
                className="bg-blue-500 h-3.5 rounded-full transition-all duration-700 ease-out relative"
                style={{ width: `${progressPercentage}%` }}
              >
                <div className="absolute inset-0 bg-white/20"></div>
              </div>
            </div>
          </div>
        </div>

        {detailLoading ? <p className="text-sm text-gray-500 mb-4">{t.fetching_rate}</p> : null}
        {detailError ? <p className="text-xs text-amber-600 mb-4">{detailError}</p> : null}

        <div className="space-y-12 pb-4">
          <div className="flex items-center justify-between">
            {stepsData.slice(0, 5).map((step, index) => renderStepCard(step, index, 5))}
          </div>
          <div className="flex items-center justify-between">
            {stepsData.slice(5, 10).map((step, index) => renderStepCard(step, index, 5))}
          </div>
        </div>
      </div>
    </div>
  );
};


