import { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  FileSearch,
  Play,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
} from 'lucide-react';
import { API_BASE_URL } from '../shared/config/api';
import { LanguageContext } from '../shared/i18n/language-context';
import { buildAuthHeaders, fetchJSON } from '../shared/utils/http';
import { useAuth } from '../shared/auth/AuthContext';

const COPY = {
  zh: {
    title: 'AI 审计与财务复核',
    subtitle: '集中查看业务审计运行、风险等级、检查项和发现问题',
    runAudit: '执行审计',
    businessId: '业务 ID',
    costRecordId: '成本记录 ID（可选）',
    businessIdRequired: '请输入业务 ID',
    refresh: '刷新',
    totalRuns: '审计运行',
    highRisk: '高风险',
    successRuns: '成功完成',
    avgScore: '平均分',
    businessList: '待审计业务列表',
    sRef: '业务编号',
    customer: '客户',
    dataStatus: '数据状态',
    auditNow: '执行审计',
    useSelected: '填入表单',
    runList: '审计运行列表',
    detail: '审计详情',
    checks: '检查项',
    findings: '发现项',
    noFindings: '暂无发现项',
    noChecks: '暂无检查项',
    selectRun: '选择左侧审计记录查看详情',
    source: '来源',
    model: '模型',
    status: '状态',
    risk: '风险',
    score: '分数',
    business: '业务',
    cost: '成本',
    created: '创建时间',
    summary: '审计摘要',
    evidence: '证据',
    suggestion: '建议',
    amount: '金额',
    empty: '暂无审计记录',
    loading: '加载中...',
    running: '审计中...',
    runSuccess: '审计已完成',
  },
  en: {
    title: 'AI Audit & Finance Review',
    subtitle: 'Review audit runs, risk levels, checks, and findings in one place',
    runAudit: 'Run Audit',
    businessId: 'Business ID',
    costRecordId: 'Cost Record ID (optional)',
    businessIdRequired: 'Enter a business ID',
    refresh: 'Refresh',
    totalRuns: 'Audit Runs',
    highRisk: 'High Risk',
    successRuns: 'Completed',
    avgScore: 'Avg Score',
    businessList: 'Business Records',
    sRef: 'Reference',
    customer: 'Customer',
    dataStatus: 'Data Status',
    auditNow: 'Run Audit',
    useSelected: 'Use',
    runList: 'Audit Runs',
    detail: 'Audit Detail',
    checks: 'Checks',
    findings: 'Findings',
    noFindings: 'No findings',
    noChecks: 'No checks',
    selectRun: 'Select an audit run on the left',
    source: 'Source',
    model: 'Model',
    status: 'Status',
    risk: 'Risk',
    score: 'Score',
    business: 'Business',
    cost: 'Cost',
    created: 'Created',
    summary: 'Summary',
    evidence: 'Evidence',
    suggestion: 'Suggestion',
    amount: 'Amount',
    empty: 'No audit runs',
    loading: 'Loading...',
    running: 'Running...',
    runSuccess: 'Audit completed',
  },
  pt: {
    title: 'Auditoria IA e Revisao Financeira',
    subtitle: 'Veja execucoes, riscos, verificacoes e apontamentos em um so lugar',
    runAudit: 'Executar Auditoria',
    businessId: 'ID do Negocio',
    costRecordId: 'ID do Custo (opcional)',
    businessIdRequired: 'Informe o ID do negocio',
    refresh: 'Atualizar',
    totalRuns: 'Auditorias',
    highRisk: 'Alto Risco',
    successRuns: 'Concluidas',
    avgScore: 'Media',
    businessList: 'Negocios para Auditoria',
    sRef: 'Referencia',
    customer: 'Cliente',
    dataStatus: 'Status dos Dados',
    auditNow: 'Auditar',
    useSelected: 'Usar',
    runList: 'Execucoes',
    detail: 'Detalhe',
    checks: 'Verificacoes',
    findings: 'Apontamentos',
    noFindings: 'Sem apontamentos',
    noChecks: 'Sem verificacoes',
    selectRun: 'Selecione uma auditoria a esquerda',
    source: 'Origem',
    model: 'Modelo',
    status: 'Status',
    risk: 'Risco',
    score: 'Pontuacao',
    business: 'Negocio',
    cost: 'Custo',
    created: 'Criado em',
    summary: 'Resumo',
    evidence: 'Evidencia',
    suggestion: 'Sugestao',
    amount: 'Valor',
    empty: 'Nenhuma auditoria',
    loading: 'Carregando...',
    running: 'Executando...',
    runSuccess: 'Auditoria concluida',
  },
};

const riskClass = (risk) => {
  const value = String(risk || '').toUpperCase();
  if (value === 'HIGH' || value === 'CRITICAL') return 'bg-red-50 text-red-700 border-red-200';
  if (value === 'MEDIUM') return 'bg-amber-50 text-amber-700 border-amber-200';
  if (value === 'LOW') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  return 'bg-gray-50 text-gray-600 border-gray-200';
};

const severityClass = (severity) => {
  const value = String(severity || '').toUpperCase();
  if (value === 'HIGH' || value === 'CRITICAL') return 'bg-red-100 text-red-700';
  if (value === 'MEDIUM') return 'bg-amber-100 text-amber-700';
  if (value === 'LOW') return 'bg-blue-100 text-blue-700';
  return 'bg-gray-100 text-gray-600';
};

const statusClass = (status) => {
  const value = String(status || '').toUpperCase();
  if (value === 'SUCCESS') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (value === 'FAILED') return 'bg-red-50 text-red-700 border-red-200';
  return 'bg-blue-50 text-blue-700 border-blue-200';
};

const fmtScore = (score) => Number(score || 0).toFixed(0);
const fmtSource = (source) => {
  const value = String(source || '').toUpperCase();
  if (value === 'LANGCHAIN_AGENT') return 'LangChain Agent';
  if (value === 'RULE') return 'Rule Engine';
  return source || '-';
};
const fmtAmount = (amount) => {
  if (amount === null || amount === undefined || amount === '') return '-';
  return `${Number(amount || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} BRL`;
};

export default function AuditReviewView() {
  const { auth } = useAuth();
  const lang = useContext(LanguageContext);
  const text = COPY[lang] || COPY.zh;
  const authToken = auth?.access_token;

  const [runs, setRuns] = useState([]);
  const [total, setTotal] = useState(0);
  const [selectedRunId, setSelectedRunId] = useState(null);
  const [selectedRun, setSelectedRun] = useState(null);
  const [businesses, setBusinesses] = useState([]);
  const [businessLoading, setBusinessLoading] = useState(false);
  const [businessError, setBusinessError] = useState('');
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState('');
  const [detailError, setDetailError] = useState('');
  const [runMessage, setRunMessage] = useState('');
  const [form, setForm] = useState({ business_id: '', cost_record_id: '' });
  const [runBusy, setRunBusy] = useState(false);
  const selectedRunIdRef = useRef(null);

  useEffect(() => {
    selectedRunIdRef.current = selectedRunId;
  }, [selectedRunId]);

  const loadDetail = useCallback(async (runId) => {
    if (!authToken || !runId) return;
    setDetailLoading(true);
    setDetailError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/audit/runs/${runId}`, {
        headers: buildAuthHeaders(authToken),
      });
      setSelectedRun(data?.run || null);
    } catch (err) {
      setDetailError(err.message || 'failed');
    } finally {
      setDetailLoading(false);
    }
  }, [authToken]);

  const loadRuns = useCallback(async (preferredRunId = null) => {
    if (!authToken) return;
    setLoading(true);
    setError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/audit/runs?limit=50&offset=0`, {
        headers: buildAuthHeaders(authToken),
      });
      const items = data?.items || [];
      setRuns(items);
      setTotal(Number(data?.total || items.length || 0));
      const currentRunId = preferredRunId || selectedRunIdRef.current;
      const stillVisible = currentRunId && items.some((item) => Number(item.id) === Number(currentRunId));
      const nextId = stillVisible ? currentRunId : items[0]?.id;
      setSelectedRunId(nextId || null);
      if (nextId) loadDetail(nextId);
      if (!nextId) setSelectedRun(null);
    } catch (err) {
      setError(err.message || 'failed');
    } finally {
      setLoading(false);
    }
  }, [authToken, loadDetail]);

  const loadBusinesses = useCallback(async () => {
    if (!authToken) return;
    setBusinessLoading(true);
    setBusinessError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/business?limit=50&offset=0`, {
        headers: buildAuthHeaders(authToken),
      });
      setBusinesses(data?.items || []);
    } catch (err) {
      setBusinessError(err.message || 'failed');
    } finally {
      setBusinessLoading(false);
    }
  }, [authToken]);

  useEffect(() => {
    loadRuns();
    loadBusinesses();
  }, [loadRuns, loadBusinesses]);

  const stats = useMemo(() => {
    const success = runs.filter((run) => String(run.status).toUpperCase() === 'SUCCESS').length;
    const high = runs.filter((run) => ['HIGH', 'CRITICAL'].includes(String(run.risk_level || '').toUpperCase())).length;
    const avg = runs.length
      ? runs.reduce((sum, run) => sum + Number(run.score || 0), 0) / runs.length
      : 0;
    return { success, high, avg };
  }, [runs]);

  const selectRun = (runId) => {
    setSelectedRunId(runId);
    loadDetail(runId);
  };

  const submitAudit = async (override = null) => {
    if (!authToken || runBusy) return;
    const businessId = String(override?.business_id ?? form.business_id ?? '').trim();
    const costRecordId = String(override?.cost_record_id ?? form.cost_record_id ?? '').trim();
    if (!businessId) {
      setRunMessage(text.businessIdRequired);
      return;
    }

    setRunBusy(true);
    setRunMessage('');
    try {
      const payload = costRecordId ? { cost_record_id: Number(costRecordId) } : {};
      const data = await fetchJSON(`${API_BASE_URL}/api/audit/business/${Number(businessId)}/run`, {
        method: 'POST',
        headers: buildAuthHeaders(authToken, { 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload),
      });
      const run = data?.run;
      setRunMessage(text.runSuccess);
      if (run?.id) {
        setSelectedRunId(run.id);
        setSelectedRun(run);
      }
      setForm({ business_id: '', cost_record_id: '' });
      loadRuns(run?.id || null);
    } catch (err) {
      setRunMessage(err.message || 'failed');
    } finally {
      setRunBusy(false);
    }
  };

  const checks = selectedRun?.checks || [];
  const findings = selectedRun?.findings || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-blue-600 mb-2">
            <ClipboardCheck className="w-5 h-5" />
            <span className="text-xs font-semibold uppercase tracking-wider">{text.source}</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">{text.title}</h2>
          <p className="text-sm text-gray-500 mt-1">{text.subtitle}</p>
        </div>

        <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-3 flex flex-col lg:flex-row gap-2 lg:items-center">
          <input
            value={form.business_id}
            onChange={(e) => setForm((prev) => ({ ...prev, business_id: e.target.value }))}
            placeholder={text.businessId}
            type="number"
            className="w-full lg:w-32 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
          <input
            value={form.cost_record_id}
            onChange={(e) => setForm((prev) => ({ ...prev, cost_record_id: e.target.value }))}
            placeholder={text.costRecordId}
            type="number"
            className="w-full lg:w-44 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
          <button
            type="button"
            onClick={submitAudit}
            disabled={runBusy}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-60"
          >
            <Play className="w-4 h-4" />
            {runBusy ? text.running : text.runAudit}
          </button>
          <button
            type="button"
            onClick={loadRuns}
            className="inline-flex items-center justify-center gap-2 px-3 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {text.refresh}
          </button>
        </div>
      </div>

      {runMessage ? <p className="text-sm text-amber-600">{runMessage}</p> : null}
      {error ? <p className="text-sm text-amber-600">{error}</p> : null}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard icon={FileSearch} label={text.totalRuns} value={total} color="blue" />
        <StatCard icon={ShieldAlert} label={text.highRisk} value={stats.high} color="red" />
        <StatCard icon={CheckCircle2} label={text.successRuns} value={stats.success} color="emerald" />
        <StatCard icon={ShieldCheck} label={text.avgScore} value={fmtScore(stats.avg)} color="amber" />
      </div>

      <section className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/60">
          <h3 className="font-bold text-gray-800">{text.businessList}</h3>
          <button
            type="button"
            onClick={loadBusinesses}
            className="inline-flex items-center gap-2 px-3 py-1.5 border border-gray-200 text-gray-600 rounded-lg text-xs font-medium hover:bg-white"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${businessLoading ? 'animate-spin' : ''}`} />
            {text.refresh}
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-gray-500 bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-5 py-3 font-semibold">ID</th>
                <th className="px-5 py-3 font-semibold">{text.sRef}</th>
                <th className="px-5 py-3 font-semibold">{text.customer}</th>
                <th className="px-5 py-3 font-semibold">{text.dataStatus}</th>
                <th className="px-5 py-3 font-semibold text-right">{text.auditNow}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {businesses.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-5 py-8 text-center text-gray-400">
                    {businessLoading ? text.loading : businessError || '-'}
                  </td>
                </tr>
              ) : businesses.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-4 font-semibold text-gray-900">#{item.id}</td>
                  <td className="px-5 py-4">
                    <div className="font-medium text-gray-800">{item.s_ref || '-'}</div>
                    <div className="text-xs text-gray-400">{item.invoice_no || item.n_ref || '-'}</div>
                  </td>
                  <td className="px-5 py-4 text-gray-600">{item.customer_name || '-'}</td>
                  <td className="px-5 py-4">
                    <span className="inline-flex px-2.5 py-1 rounded-full border text-xs font-semibold bg-blue-50 text-blue-700 border-blue-100">
                      {item.data_status || '-'}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => setForm((prev) => ({ ...prev, business_id: String(item.id) }))}
                        className="px-3 py-1.5 border border-gray-200 text-gray-600 rounded-lg text-xs font-medium hover:bg-gray-50"
                      >
                        {text.useSelected}
                      </button>
                      <button
                        type="button"
                        disabled={runBusy}
                        onClick={() => submitAudit({ business_id: item.id })}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 disabled:opacity-60"
                      >
                        <Play className="w-3.5 h-3.5" />
                        {runBusy ? text.running : text.auditNow}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {businessError && businesses.length > 0 ? <p className="px-6 py-3 text-xs text-amber-600">{businessError}</p> : null}
      </section>

      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.05fr)_minmax(420px,0.95fr)] gap-6">
        <section className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/60">
            <h3 className="font-bold text-gray-800">{text.runList}</h3>
            {loading ? <span className="text-xs text-gray-400">{text.loading}</span> : null}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-500 bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="px-5 py-3 font-semibold">{text.business}</th>
                  <th className="px-5 py-3 font-semibold">{text.risk}</th>
                  <th className="px-5 py-3 font-semibold">{text.score}</th>
                  <th className="px-5 py-3 font-semibold">{text.status}</th>
                  <th className="px-5 py-3 font-semibold">{text.created}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {runs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-8 text-center text-gray-400">{loading ? text.loading : text.empty}</td>
                  </tr>
                ) : runs.map((run) => (
                  <tr
                    key={run.id}
                    onClick={() => selectRun(run.id)}
                    className={`cursor-pointer transition-colors ${Number(selectedRunId) === Number(run.id) ? 'bg-blue-50/70' : 'hover:bg-gray-50'}`}
                  >
                    <td className="px-5 py-4">
                      <div className="font-semibold text-gray-900">#{run.business_id}</div>
                      <div className="text-xs text-gray-400">{text.cost}: {run.cost_record_id || '-'}</div>
                    </td>
                    <td className="px-5 py-4">
                      <span className={`inline-flex px-2.5 py-1 rounded-full border text-xs font-semibold ${riskClass(run.risk_level)}`}>
                        {run.risk_level || '-'}
                      </span>
                    </td>
                    <td className="px-5 py-4 font-semibold text-gray-800">{fmtScore(run.score)}</td>
                    <td className="px-5 py-4">
                      <span className={`inline-flex px-2.5 py-1 rounded-full border text-xs font-semibold ${statusClass(run.status)}`}>
                        {run.status || '-'}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-gray-500 whitespace-nowrap">{run.created_time || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/60 flex items-center justify-between">
            <h3 className="font-bold text-gray-800">{text.detail}</h3>
            {selectedRun ? (
              <span className={`inline-flex px-2.5 py-1 rounded-full border text-xs font-semibold ${riskClass(selectedRun.risk_level)}`}>
                {selectedRun.risk_level || '-'}
              </span>
            ) : null}
          </div>

          {!selectedRun ? (
            <div className="p-10 text-center text-gray-400">
              <FileSearch className="w-10 h-10 mx-auto mb-3 text-gray-300" />
              {detailLoading ? text.loading : text.selectRun}
            </div>
          ) : (
            <div className="p-6 space-y-6">
              {detailError ? <p className="text-sm text-amber-600">{detailError}</p> : null}
              <div>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-xs text-gray-400 mb-1">Run #{selectedRun.id}</div>
                    <h4 className="text-lg font-bold text-gray-900">{text.business} #{selectedRun.business_id}</h4>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-gray-900">{fmtScore(selectedRun.score)}</div>
                    <div className="text-xs text-gray-400">{text.score}</div>
                  </div>
                </div>
                <p className="mt-4 text-sm text-gray-600 leading-relaxed bg-gray-50 border border-gray-100 rounded-xl p-4">
                  {selectedRun.summary || '-'}
                </p>
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
                <MiniMeta label={text.source} value={fmtSource(selectedRun.source)} />
                <MiniMeta label={text.model} value={selectedRun.model_name || '-'} />
                <MiniMeta label={text.status} value={selectedRun.status || '-'} />
                <MiniMeta label={text.created} value={selectedRun.created_time || '-'} />
              </div>

              <div>
                <h4 className="font-semibold text-gray-800 mb-3">{text.checks}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {checks.length === 0 ? (
                    <div className="text-sm text-gray-400">{text.noChecks}</div>
                  ) : checks.map((check, index) => (
                    <div key={`${check.code || check.name || index}`} className="border border-gray-100 rounded-xl p-3 bg-gray-50/50">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-medium text-gray-800 text-sm">{check.name || check.code || '-'}</span>
                        <span className={`text-[11px] px-2 py-0.5 rounded-full ${check.status === 'PASS' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                          {check.status || '-'}
                        </span>
                      </div>
                      {check.code ? <div className="text-xs text-gray-400 mt-1">{check.code}</div> : null}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-800 mb-3">{text.findings}</h4>
                <div className="space-y-3">
                  {findings.length === 0 ? (
                    <div className="flex items-center gap-2 text-sm text-emerald-600 bg-emerald-50 border border-emerald-100 rounded-xl p-4">
                      <CheckCircle2 className="w-4 h-4" />
                      {text.noFindings}
                    </div>
                  ) : findings.map((finding) => (
                    <div key={finding.id} className="border border-gray-100 rounded-xl p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <div className="mt-0.5 w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                            <AlertTriangle className="w-4 h-4" />
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">{finding.title}</div>
                            <div className="text-xs text-gray-400 mt-1">{finding.rule_code || finding.finding_type || '-'}</div>
                          </div>
                        </div>
                        <span className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-semibold ${severityClass(finding.severity)}`}>
                          {finding.severity || '-'}
                        </span>
                      </div>
                      {finding.description ? <p className="text-sm text-gray-600 mt-3 leading-relaxed">{finding.description}</p> : null}
                      <div className="mt-3 grid grid-cols-1 gap-2 text-xs">
                        {finding.evidence ? <InfoLine label={text.evidence} value={finding.evidence} /> : null}
                        {finding.suggestion ? <InfoLine label={text.suggestion} value={finding.suggestion} /> : null}
                        <InfoLine label={text.amount} value={fmtAmount(finding.amount)} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  const palette = {
    blue: 'bg-blue-50 text-blue-600',
    red: 'bg-red-50 text-red-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
  };
  const IconComponent = icon;
  return (
    <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-5 flex items-center justify-between">
      <div>
        <div className="text-xs font-medium text-gray-400">{label}</div>
        <div className="text-2xl font-bold text-gray-900 mt-1">{value}</div>
      </div>
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${palette[color] || palette.blue}`}>
        <IconComponent className="w-5 h-5" />
      </div>
    </div>
  );
}

function MiniMeta({ label, value }) {
  return (
    <div className="rounded-xl border border-gray-100 bg-gray-50 p-3 min-w-0">
      <div className="text-xs text-gray-400 mb-1">{label}</div>
      <div className="font-semibold text-gray-800 truncate">{value}</div>
    </div>
  );
}

function InfoLine({ label, value }) {
  return (
    <div className="bg-gray-50 rounded-lg px-3 py-2 text-gray-600">
      <span className="font-semibold text-gray-700">{label}: </span>
      {value}
    </div>
  );
}
