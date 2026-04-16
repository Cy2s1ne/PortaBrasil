import { useEffect, useState } from 'react';
import { Calculator, Download, PieChart, Plus, RefreshCw, Trash2 } from 'lucide-react';
import { API_BASE_URL } from '../shared/config/api';
import { useT } from '../shared/i18n/language-context';
import { formatCurrencyBRL } from '../shared/utils/format';
import { buildAuthHeaders, fetchJSON } from '../shared/utils/http';

export default function CostAnalysisView({ authToken }) {
  const t = useT();
  const [customsFee, setCustomsFee] = useState('');
  const [refundFee, setRefundFee] = useState('');
  const [usdAmount, setUsdAmount] = useState('');
  const [usdRate, setUsdRate] = useState('');
  const [rateLoading, setRateLoading] = useState(false);
  const [rateError, setRateError] = useState('');
  const [rateUpdatedAt, setRateUpdatedAt] = useState('');
  const [otherFees, setOtherFees] = useState('');
  const [products, setProducts] = useState([{ name: '', qty: '' }]);
  const [result, setResult] = useState(null);
  const [overview, setOverview] = useState(null);
  const [calcLoading, setCalcLoading] = useState(false);
  const [calcError, setCalcError] = useState('');

  const fetchOverview = async () => {
    if (!authToken) return;
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/cost/overview`, {
        headers: buildAuthHeaders(authToken),
      });
      setOverview(data || null);
    } catch (err) {
      setCalcError(err.message || 'failed');
    }
  };

  const fetchRate = async () => {
    if (!authToken) return;
    setRateLoading(true);
    setRateError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/cost/exchange-rate?base=USD&quote=BRL`, {
        headers: buildAuthHeaders(authToken),
      });
      setUsdRate(String(data?.rate ?? ''));
      setRateUpdatedAt(data?.updated_at || '');
      if (data?.warning) {
        setRateError(data.warning);
      }
    } catch (err) {
      setRateError(err.message || t.rate_network_failed);
    } finally {
      setRateLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
    fetchRate();
  }, [authToken]);

  const addProduct = () => setProducts((prev) => [...prev, { name: '', qty: '' }]);
  const removeProduct = (i) => setProducts((prev) => prev.filter((_, idx) => idx !== i));
  const updateProduct = (i, field, value) =>
    setProducts((prev) => prev.map((p, idx) => (idx === i ? { ...p, [field]: value } : p)));

  const fmt = (num) => Number(num || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 4 });

  const calculate = async () => {
    if (!authToken) return;
    setCalcLoading(true);
    setCalcError('');
    try {
      const payload = {
        customs_fee: Number(customsFee || 0),
        refund_fee: Number(refundFee || 0),
        usd_amount: Number(usdAmount || 0),
        usd_rate: Number(usdRate || 0),
        other_fees: Number(otherFees || 0),
        products: products.map((p) => ({ name: p.name || '', qty: Number(p.qty || 0) })),
      };
      const data = await fetchJSON(`${API_BASE_URL}/api/cost/calculate`, {
        method: 'POST',
        headers: buildAuthHeaders(authToken, { 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload),
      });
      setResult({
        cf: Number(data?.input?.customs_fee || 0),
        rf: Number(data?.input?.refund_fee || 0),
        ua: Number(data?.input?.usd_amount || 0),
        ur: Number(data?.input?.usd_rate || 0),
        of: Number(data?.input?.other_fees || 0),
        netCustoms: Number(data?.summary?.net_customs || 0),
        usdInBrl: Number(data?.summary?.usd_in_brl || 0),
        totalBase: Number(data?.summary?.total_base || 0),
        totalQty: Number(data?.summary?.total_qty || 0),
        perUnitCost: Number(data?.summary?.per_unit_cost || 0),
        productCosts: (data?.product_costs || []).map((p) => ({
          name: p.name || t.unnamed_product,
          qty: Number(p.qty || 0),
          cost: Number(p.cost || 0),
          unitCost: Number(p.unit_cost || 0),
        })),
      });
    } catch (err) {
      setCalcError(err.message || 'failed');
    } finally {
      setCalcLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setCustomsFee('');
    setRefundFee('');
    setUsdAmount('');
    setOtherFees('');
    setProducts([{ name: '', qty: '' }]);
    setCalcError('');
  };

  const inputCls = "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-colors";
  const labelCls = "block text-xs font-medium text-gray-500 mb-1.5";
  const sectionCls = "bg-white rounded-2xl shadow-sm border border-gray-100 p-6";
  const topTotal = Number(overview?.total_import_cost || 0);
  const majorTaxDetails = (overview?.major_tax_details || []).length ? (overview?.major_tax_details || []) : [
    { label: 'II (进口税)', amount: 520000, percent: 42 },
    { label: 'IPI (工业产品税)', amount: 310000, percent: 25 },
    { label: 'PIS/COFINS', amount: 250000, percent: 20 },
    { label: 'ICMS', amount: 115600, percent: 9 },
    { label: t.afrmm, amount: 50000, percent: 4 },
  ];
  const barColors = ['bg-blue-500', 'bg-orange-400', 'bg-green-400', 'bg-purple-500', 'bg-gray-400'];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-bold text-gray-800 mb-5">{t.cost_structure_title}</h2>
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="lg:w-1/3 bg-gray-50 rounded-xl p-6 flex flex-col items-center justify-center border border-gray-100">
            <div className="text-gray-500 mb-1 text-sm font-medium">{t.total_import_cost}</div>
            <div className="text-3xl font-bold text-gray-800 mb-5">{formatCurrencyBRL(topTotal)}</div>
            <div className="relative w-40 h-40 rounded-full border-[14px] border-blue-500 flex items-center justify-center">
              <div className="absolute inset-0 border-[14px] border-orange-400 rounded-full" style={{ clipPath: 'polygon(50% 50%, 100% 0, 100% 100%, 0 100%, 0 50%)' }}></div>
              <div className="absolute inset-0 border-[14px] border-green-400 rounded-full" style={{ clipPath: 'polygon(50% 50%, 0 50%, 0 0, 50% 0)' }}></div>
              <div className="bg-gray-50 w-full h-full rounded-full absolute -z-10"></div>
              <div className="text-center z-10">
                <div className="text-xs text-gray-500">{t.largest_share}</div>
                <div className="font-bold text-gray-800 text-sm">{overview?.largest_share?.label || 'II (进口税)'}</div>
              </div>
            </div>
          </div>
          <div className="lg:w-2/3 space-y-4">
            <h3 className="font-semibold text-gray-800 border-b border-gray-100 pb-2 text-sm">{t.major_tax_details}</h3>
            {majorTaxDetails.map((item, i) => (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium text-gray-700">{item.label}</span>
                  <span className="font-bold text-gray-800">{formatCurrencyBRL(item.amount)}</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div className={`${barColors[i % barColors.length]} h-2 rounded-full`} style={{ width: `${item.percent || 0}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className={sectionCls}>
            <div className="flex items-center mb-4">
              <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold mr-2">1</div>
              <h3 className="font-semibold text-gray-800">{t.customs_fees_section}</h3>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelCls}>{t.total_customs_fee}</label>
                <input type="number" placeholder="0.00" value={customsFee} onChange={(e) => setCustomsFee(e.target.value)} className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>{t.refund_fee}</label>
                <input type="number" placeholder="0.00" value={refundFee} onChange={(e) => setRefundFee(e.target.value)} className={inputCls} />
              </div>
            </div>
          </div>

          <div className={sectionCls}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold mr-2">2</div>
                <h3 className="font-semibold text-gray-800">{t.product_info_section}</h3>
              </div>
              <button onClick={addProduct} className="flex items-center text-xs font-medium text-blue-600 hover:text-blue-700 px-2.5 py-1.5 rounded-lg hover:bg-blue-50 transition-colors border border-blue-200">
                <Plus className="w-3.5 h-3.5 mr-1" /> {t.add_product}
              </button>
            </div>
            <div className="space-y-2.5">
              {products.map((p, i) => (
                <div key={i} className="flex items-center space-x-2">
                  <input type="text" placeholder={t.product_name_ph} value={p.name} onChange={(e) => updateProduct(i, 'name', e.target.value)} className={`${inputCls} flex-1`} />
                  <input type="number" placeholder={t.qty_ph} value={p.qty} onChange={(e) => updateProduct(i, 'qty', e.target.value)} className={`${inputCls} w-24`} />
                  {products.length > 1 && (
                    <button onClick={() => removeProduct(i)} className="p-2 text-gray-300 hover:text-red-400 hover:bg-red-50 rounded-lg transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className={sectionCls}>
            <div className="flex items-center mb-4">
              <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold mr-2">3</div>
              <h3 className="font-semibold text-gray-800">{t.additional_fees_section}</h3>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className={labelCls}>{t.usd_amount}</label>
                <input type="number" placeholder="0.00" value={usdAmount} onChange={(e) => setUsdAmount(e.target.value)} className={inputCls} />
              </div>
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className={`${labelCls} mb-0`}>{t.usd_rate_label}</label>
                  <button
                    onClick={fetchRate}
                    disabled={rateLoading}
                    className="flex items-center text-[11px] text-blue-500 hover:text-blue-700 disabled:text-gray-300 transition-colors"
                  >
                    <RefreshCw className={`w-3 h-3 mr-0.5 ${rateLoading ? 'animate-spin' : ''}`} />
                    {rateLoading ? t.fetching_rate : t.refresh_rate}
                  </button>
                </div>
                <div className="relative">
                  <input
                    type="number"
                    placeholder={t.auto_fetching_ph}
                    value={usdRate}
                    onChange={(e) => setUsdRate(e.target.value)}
                    className={`${inputCls} pr-16`}
                  />
                  {rateLoading && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-blue-400 font-medium">{t.fetching_in}</span>
                  )}
                  {!rateLoading && usdRate && !rateError && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-green-500 font-medium">{t.realtime_tag}</span>
                  )}
                  {!rateLoading && rateError && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-orange-400 font-medium">{t.manual_tag}</span>
                  )}
                </div>
                {rateUpdatedAt && !rateError && (
                  <div className="text-[10px] text-gray-400 mt-1">{t.updated_at}{rateUpdatedAt}</div>
                )}
                {rateError && (
                  <div className="text-[10px] text-orange-400 mt-1">{rateError}</div>
                )}
              </div>
              <div>
                <label className={labelCls}>{t.other_fees_label}</label>
                <input type="number" placeholder="0.00" value={otherFees} onChange={(e) => setOtherFees(e.target.value)} className={inputCls} />
              </div>
            </div>
          </div>

          <button onClick={calculate} disabled={calcLoading} className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold flex items-center justify-center space-x-2 shadow-sm transition-colors disabled:opacity-60">
            <Calculator className="w-5 h-5" />
            <span>{calcLoading ? t.fetching_rate : t.calculate_cost}</span>
          </button>
          {calcError ? <p className="text-xs text-amber-600">{calcError}</p> : null}
        </div>

        <div className="space-y-4">
          {!result ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center h-full min-h-[400px] text-center p-8">
              <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4 border border-gray-100">
                <Calculator className="w-8 h-8 text-gray-300" />
              </div>
              <p className="text-gray-400 font-medium">{t.fill_data_prompt}</p>
              <p className="text-gray-300 text-sm mt-1">{t.click_calc_prompt}</p>
            </div>
          ) : (
            <>
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white">
                <div className="flex items-center mb-4">
                  <PieChart className="w-4 h-4 mr-2 opacity-80" />
                  <span className="text-sm font-semibold opacity-90">{t.cost_summary}</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-2xl font-bold">{fmt(result.totalBase)} BRL</div>
                    <div className="text-blue-200 text-xs mt-1">{t.container_total_cost}</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">{fmt(result.perUnitCost)} BRL</div>
                    <div className="text-blue-200 text-xs mt-1">{t.per_item_cost}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <span className="w-1 h-4 bg-blue-500 rounded mr-2 inline-block"></span>{t.formula_title}
                </h4>
                <div className="bg-blue-50 rounded-xl p-4 text-xs text-blue-800 leading-relaxed font-mono">
                  {t.formula_text}
                </div>
                <div className="mt-3 bg-gray-50 rounded-xl p-4 text-xs text-gray-600 leading-loose font-mono">
                  = ({fmt(result.cf)} − {fmt(result.rf)} + {fmt(result.usdInBrl)} + {fmt(result.of)}) ÷ {result.totalQty}<br />
                  = {fmt(result.totalBase)} ÷ {result.totalQty}<br />
                  = <span className="font-bold text-gray-800">{fmt(result.perUnitCost)} BRL/{t.pcs}</span>
                </div>
              </div>

              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <span className="w-1 h-4 bg-indigo-500 rounded mr-2 inline-block"></span>{t.cost_breakdown}
                </h4>
                <div className="space-y-2 text-sm">
                  {[
                    { label: t.customs_fee_row, value: `${fmt(result.cf)} BRL`, normal: true },
                    { label: t.refund_fee_row, value: `−${fmt(result.rf)} BRL`, red: true },
                    { label: t.net_customs_row, value: `${fmt(result.netCustoms)} BRL`, bold: true },
                    { label: t.exchange_rate_row, value: `1 USD = ${result.ur} BRL`, normal: true },
                    { label: t.usd_converted_row, value: `${fmt(result.usdInBrl)} BRL`, normal: true },
                    { label: t.other_fees_row, value: `${fmt(result.of)} BRL`, normal: true },
                    { label: t.total_cost_base_row, value: `${fmt(result.totalBase)} BRL`, bold: true, border: true },
                  ].map((row, i) => (
                    <div key={i} className={`flex justify-between py-1.5 ${row.border ? 'border-t border-gray-200 mt-1 pt-2.5' : ''}`}>
                      <span className={`${row.bold ? 'font-semibold text-gray-800' : 'text-gray-500'}`}>{row.label}</span>
                      <span className={`font-medium ${row.bold ? 'text-gray-900 font-bold' : row.red ? 'text-red-500' : 'text-gray-700'}`}>{row.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <span className="w-1 h-4 bg-green-500 rounded mr-2 inline-block"></span>{t.product_cost_detail}
                </h4>
                <div className="space-y-2">
                  {result.productCosts.map((p, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100">
                      <div>
                        <div className="font-semibold text-gray-800 text-sm">{p.name}</div>
                        <div className="text-xs text-gray-400 mt-0.5">{t.qty_label_detail}{p.qty} {t.pcs}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-gray-800 text-sm">{fmt(p.cost)} BRL</div>
                        <div className="text-xs text-gray-400 mt-0.5">{fmt(p.unitCost)} {t.per_unit}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex space-x-3">
                <button onClick={reset} className="flex-1 py-2.5 border border-gray-200 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                  {t.reset}
                </button>
                <button className="flex-1 py-2.5 border border-blue-200 text-blue-600 rounded-xl text-sm font-semibold hover:bg-blue-50 transition-colors flex items-center justify-center">
                  <Download className="w-4 h-4 mr-1.5" /> {t.export_pdf}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

