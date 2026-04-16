import React, { useState, useEffect, useRef, createContext, useContext } from 'react';
import LoginPage from './LoginPage';
import {
  Home,
  UploadCloud,
  Map as MapIcon,
  PieChart,
  BarChart2,
  CheckCircle2,
  Circle,
  ArrowRight,
  Layers,
  Bell,
  Search,
  FileText,
  AlertTriangle,
  TrendingUp,
  DollarSign,
  Calendar,
  MoreVertical,
  Upload,
  FileCheck,
  Clock,
  ChevronRight,
  Download,
  Edit2,
  X,
  Plus,
  Trash2,
  Calculator,
  RefreshCw,
  Globe,
  LogOut
} from 'lucide-react';

// --- 多语言 ---
const TRANSLATIONS = {
  zh: {
    appName: '巴西海关报关系统',
    nav_home: '首页', nav_upload: '文档上传', nav_process: '流程跟踪', nav_cost: '成本分析', nav_report: '报表分析',
    system: '系统', globalSearch: '全局搜索...', admin: '超级管理员',
    needHelp: '需要帮助？', helpDesc: '查看巴西清关操作指南', contactSupport: '联系客服',
    welcome: '欢迎回来，超级管理员！',
    welcomeSub: (c, i) => `今日有 ${c} 个集装箱需要处理，${i} 个海关查验通知。`,
    newDeclaration: '新建报关单',
    stat_inProgress: '进行中任务', stat_taxes: '待缴税费', stat_anomaly: '异常/查验', stat_done: '本月已完成',
    kanban_title: '集装箱流程看板', kanban_desc: '各流程节点实时集装箱数量统计',
    kanban_unit: '个集装箱', kanban_total: '总计：', kanban_normal: '正常流转：', kanban_anomaly_label: '异常/查验：', kanban_viewAll: '查看全部',
    step1: '货物到港确认', step2: '海关申报', step3: '文件审核',
    step4: '税费计算', step5: '税费缴纳', step6: '海关查验',
    step7: '放行通知', step8: '提货准备', step9: '货物提取', step10: '运输配送',
    step1_desc: '确认集装箱已到达港口\n(自动完成)', step2_desc: '向海关提交进口申报\n(自动完成)',
    step3_desc: '海关审核提交的文件和单据', step4_desc: '计算应缴纳的关税和税费',
    step5_desc: '支付海关税费和相关费用', step6_desc: '海关对货物进行检查验证',
    step7_desc: '海关签发货物放行通知', step8_desc: '准备提货所需文件和手续',
    step9_desc: '从港口或仓库提取货物', step10_desc: '将货物运输到最终目的地',
    activity_title: '最新动态',
    act1_title: '海关查验通知', act1_desc: '集装箱号 TCNU8473629 被抽中例行查验。', act1_time: '10分钟前',
    act2_title: '税费计算完成', act2_desc: '提单号 BR2023082401 关税已计算完成，等待支付。', act2_time: '2小时前',
    act3_title: '文件审核通过', act3_desc: '商业发票和装筱单已通过巴西海关审核系统 (Siscomex)。', act3_time: '昨天 15:30',
    upload_title: '报关单据上传', upload_drag: '点击或将文件拖拽到这里上传',
    upload_formats: '支持 PDF, JPG, PNG 格式，单个文件不超过 10MB', browse: '浏览文件',
    recent_uploads: '最近上传文件', verified: '已验证', ai_processing: 'AI 识别中...',
    process_list_title: '清关流程 — 提单列表', process_list_desc: '点击「查看流程」进入该提单的流程跟踪详情',
    search_placeholder: '搜索提单号或货名...', filter: '筛选',
    bl_number: '提单号 (B/L)', goods_desc: '货物描述', declaration_date: '申报日期', port_col: '港口', status_col: '状态', action_col: '操作',
    view_process: '查看流程', status_cleared: '已放行', status_processing: '处理中', status_inspection: '海关查验',
    total_records: (n) => `共 ${n} 条记录`, prev_page: '上一页', next_page: '下一页',
    back_to_list: '返回列表', container_title: '集装箱进口流程状态', bl_label: '提单: ', export_progress: '导出进度',
    overall_progress: '整体进度：', current_step_label: '当前步骤：', all_done: '全部完成 ✓',
    edit_step_title: '编辑流程步骤状态', step_name_label: '步骤名称', status_label: '状态',
    completion_time_label: '完成时间', completion_time_hint: '(可选，如：08-24 08:10)', completion_time_ph: '输入完成时间...',
    step_desc_label: '步骤描述', cancel: '取消', save_update: '保存更新', save_success: '保存成功！',
    goods1: '工业机械零件', goods2: '电子消费产品', goods3: '纺织原材料', goods4: '医疗器械设备', goods5: '汽车零配件',
    cost_structure_title: '报关成本结构 (本月)', total_import_cost: '总进口成本', largest_share: '最大占比', major_tax_details: '主要税费明细',
    customs_fees_section: '海关费用', total_customs_fee: '海关总费用 (BRL)', refund_fee: '退款费用 (BRL)',
    product_info_section: '商品信息', add_product: '添加商品', product_name_ph: '商品名称', qty_ph: '数量',
    additional_fees_section: '附加费用', usd_amount: '美元金额 (USD)', usd_rate_label: '美元汇率 (1 USD = ? BRL)',
    refresh_rate: '刷新', fetching_rate: '获取中...', realtime_tag: '实时', manual_tag: '手动',
    other_fees_label: '其它附加费用 (BRL)', auto_fetching_ph: '自动获取中...', updated_at: '更新于 ',
    calculate_cost: '计算成本', fill_data_prompt: '请填写左侧数据', click_calc_prompt: '点击「计算成本」查看结果',
    cost_summary: '成本汇总', container_total_cost: '集装箱总成本', per_item_cost: '每件商品成本',
    formula_title: '计算公式', formula_text: '每件商品的海关成本 = (海关总费用 − 退款费用 + 折合美元费用 + 其它附加费用) ÷ 商品总数量',
    cost_breakdown: '成本分解', customs_fee_row: '海关总费用', refund_fee_row: '退款费用', net_customs_row: '净海关费用',
    exchange_rate_row: '美元汇率', usd_converted_row: '折合美元费用', other_fees_row: '其它附加费用', total_cost_base_row: '总成本基数',
    product_cost_detail: '商品成本明细', qty_label_detail: '数量：', pcs: '件', per_unit: 'BRL/件',
    reset: '重置', export_pdf: '导出 PDF', unnamed_product: '未命名商品',
    rate_parse_failed: '解析汇率失败', rate_network_failed: '网络请求失败，请手动输入',
    recent_records_title: '近期清关记录', details: '详情', afrmm: 'AFRMM 及其他',
    fetching_in: '获取中',
  },
  en: {
    appName: 'Brazil Customs System',
    nav_home: 'Home', nav_upload: 'Doc Upload', nav_process: 'Process Tracking', nav_cost: 'Cost Analysis', nav_report: 'Reports',
    system: 'System', globalSearch: 'Search...', admin: 'Super Admin',
    needHelp: 'Need Help?', helpDesc: 'View Brazil Customs Guide', contactSupport: 'Contact Support',
    welcome: 'Welcome back, Super Admin!',
    welcomeSub: (c, i) => `Today: ${c} containers to process, ${i} customs inspection notice(s).`,
    newDeclaration: 'New Declaration',
    stat_inProgress: 'In Progress', stat_taxes: 'Taxes Due', stat_anomaly: 'Anomaly/Inspection', stat_done: 'Completed This Month',
    kanban_title: 'Container Process Board', kanban_desc: 'Real-time container count per process node',
    kanban_unit: 'containers', kanban_total: 'Total: ', kanban_normal: 'Normal Flow: ', kanban_anomaly_label: 'Anomaly: ', kanban_viewAll: 'View All',
    step1: 'Arrival Confirmation', step2: 'Customs Declaration', step3: 'Document Review',
    step4: 'Tax Calculation', step5: 'Tax Payment', step6: 'Customs Inspection',
    step7: 'Release Notice', step8: 'Pickup Preparation', step9: 'Cargo Pickup', step10: 'Transport & Delivery',
    step1_desc: 'Confirm container arrived at port\n(Auto)', step2_desc: 'Submit import declaration\n(Auto)',
    step3_desc: 'Customs reviews submitted documents', step4_desc: 'Calculate duties and taxes',
    step5_desc: 'Pay customs duties and fees', step6_desc: 'Customs inspection of cargo',
    step7_desc: 'Customs issues cargo release notice', step8_desc: 'Prepare documents for pickup',
    step9_desc: 'Retrieve cargo from port or warehouse', step10_desc: 'Transport cargo to final destination',
    activity_title: 'Recent Activity',
    act1_title: 'Customs Inspection Notice', act1_desc: 'Container TCNU8473629 selected for routine inspection.', act1_time: '10 min ago',
    act2_title: 'Tax Calculation Complete', act2_desc: 'B/L BR2023082401 duties calculated, pending payment.', act2_time: '2 hours ago',
    act3_title: 'Documents Approved', act3_desc: 'Commercial invoice and packing list approved by Siscomex.', act3_time: 'Yesterday 15:30',
    upload_title: 'Customs Document Upload', upload_drag: 'Click or drag files here to upload',
    upload_formats: 'Supports PDF, JPG, PNG. Max 10MB per file.', browse: 'Browse Files',
    recent_uploads: 'Recently Uploaded Files', verified: 'Verified', ai_processing: 'AI Processing...',
    process_list_title: 'Clearance Process — B/L List', process_list_desc: 'Click “View Process” to enter process tracking',
    search_placeholder: 'Search B/L or cargo...', filter: 'Filter',
    bl_number: 'B/L Number', goods_desc: 'Cargo Description', declaration_date: 'Declaration Date', port_col: 'Port', status_col: 'Status', action_col: 'Action',
    view_process: 'View Process', status_cleared: 'Cleared', status_processing: 'Processing', status_inspection: 'Inspection',
    total_records: (n) => `${n} records total`, prev_page: 'Prev', next_page: 'Next',
    back_to_list: 'Back to List', container_title: 'Container Import Process Status', bl_label: 'B/L: ', export_progress: 'Export Progress',
    overall_progress: 'Overall Progress:', current_step_label: 'Current Step:', all_done: 'All Done ✓',
    edit_step_title: 'Edit Process Step Status', step_name_label: 'Step Name', status_label: 'Status',
    completion_time_label: 'Completion Time', completion_time_hint: '(optional, e.g.: 08-24 08:10)', completion_time_ph: 'Enter completion time...',
    step_desc_label: 'Step Description', cancel: 'Cancel', save_update: 'Save Update', save_success: 'Saved!',
    goods1: 'Industrial Machinery Parts', goods2: 'Consumer Electronics', goods3: 'Textile Raw Materials', goods4: 'Medical Equipment', goods5: 'Auto Parts',
    cost_structure_title: 'Customs Cost Structure (This Month)', total_import_cost: 'Total Import Cost', largest_share: 'Largest Share', major_tax_details: 'Main Tax Details',
    customs_fees_section: 'Customs Fees', total_customs_fee: 'Total Customs Fee (BRL)', refund_fee: 'Refund Fee (BRL)',
    product_info_section: 'Product Information', add_product: 'Add Product', product_name_ph: 'Product Name', qty_ph: 'Qty',
    additional_fees_section: 'Additional Fees', usd_amount: 'USD Amount', usd_rate_label: 'USD Rate (1 USD = ? BRL)',
    refresh_rate: 'Refresh', fetching_rate: 'Fetching...', realtime_tag: 'Live', manual_tag: 'Manual',
    other_fees_label: 'Other Fees (BRL)', auto_fetching_ph: 'Auto-fetching...', updated_at: 'Updated at ',
    calculate_cost: 'Calculate Cost', fill_data_prompt: 'Fill in the data on the left', click_calc_prompt: 'Click “Calculate Cost” to see results',
    cost_summary: 'Cost Summary', container_total_cost: 'Container Total Cost', per_item_cost: 'Cost Per Item',
    formula_title: 'Calculation Formula', formula_text: 'Cost per item = (Total Customs Fee − Refund + USD Equiv. + Other Fees) ÷ Total Qty',
    cost_breakdown: 'Cost Breakdown', customs_fee_row: 'Total Customs Fee', refund_fee_row: 'Refund Fee', net_customs_row: 'Net Customs Fee',
    exchange_rate_row: 'USD Exchange Rate', usd_converted_row: 'USD Equivalent (BRL)', other_fees_row: 'Other Fees', total_cost_base_row: 'Total Cost Base',
    product_cost_detail: 'Product Cost Detail', qty_label_detail: 'Qty: ', pcs: 'units', per_unit: 'BRL/unit',
    reset: 'Reset', export_pdf: 'Export PDF', unnamed_product: 'Unnamed Product',
    rate_parse_failed: 'Failed to parse exchange rate', rate_network_failed: 'Network error, enter manually',
    recent_records_title: 'Recent Clearance Records', details: 'Details', afrmm: 'AFRMM & Others',
    fetching_in: 'Fetching',
  },
  pt: {
    appName: 'Sistema Aduaneiro Brasil',
    nav_home: 'Início', nav_upload: 'Upload de Docs', nav_process: 'Rastreamento', nav_cost: 'Análise de Custos', nav_report: 'Relatórios',
    system: 'Sistema', globalSearch: 'Buscar...', admin: 'Super Administrador',
    needHelp: 'Precisa de Ajuda?', helpDesc: 'Ver guia de desembaraço', contactSupport: 'Suporte',
    welcome: 'Bem-vindo, Super Administrador!',
    welcomeSub: (c, i) => `Hoje: ${c} contêineres para processar, ${i} aviso(s) de inspeção.`,
    newDeclaration: 'Nova Declaração',
    stat_inProgress: 'Em Andamento', stat_taxes: 'Tributos Pendentes', stat_anomaly: 'Anomalia/Inspeção', stat_done: 'Concluídos no Mês',
    kanban_title: 'Painel de Processos', kanban_desc: 'Contagem em tempo real por etapa do processo',
    kanban_unit: 'contêineres', kanban_total: 'Total: ', kanban_normal: 'Fluxo Normal: ', kanban_anomaly_label: 'Anomalia: ', kanban_viewAll: 'Ver Todos',
    step1: 'Confirmação de Chegada', step2: 'Declaração Aduaneira', step3: 'Revisão de Documentos',
    step4: 'Cálculo de Tributos', step5: 'Pagamento de Tributos', step6: 'Inspeção Aduaneira',
    step7: 'Aviso de Liberação', step8: 'Preparo para Retirada', step9: 'Retirada da Carga', step10: 'Transporte e Entrega',
    step1_desc: 'Confirmar chegada do contêiner ao porto\n(Automático)', step2_desc: 'Submeter declaração de importação\n(Automático)',
    step3_desc: 'Revisão de documentos pela alfândega', step4_desc: 'Calcular tributos aplicáveis',
    step5_desc: 'Pagar tributos e taxas aduaneiras', step6_desc: 'Inspeção da carga pela alfândega',
    step7_desc: 'Emissão do aviso de liberação', step8_desc: 'Preparar documentação para retirada',
    step9_desc: 'Retirar carga do porto ou armazém', step10_desc: 'Transportar carga ao destino final',
    activity_title: 'Atividades Recentes',
    act1_title: 'Aviso de Inspeção', act1_desc: 'Contêiner TCNU8473629 selecionado para inspeção.', act1_time: 'Há 10 min',
    act2_title: 'Cálculo Concluído', act2_desc: 'CE BR2023082401 calculado, aguardando pagamento.', act2_time: 'Há 2 horas',
    act3_title: 'Documentos Aprovados', act3_desc: 'Fatura e romaneio aprovados pelo Siscomex.', act3_time: 'Ontem 15:30',
    upload_title: 'Upload de Documentos Aduaneiros', upload_drag: 'Clique ou arraste arquivos aqui',
    upload_formats: 'Suporta PDF, JPG, PNG. Máx. 10MB por arquivo.', browse: 'Procurar Arquivos',
    recent_uploads: 'Arquivos Recentes', verified: 'Verificado', ai_processing: 'Processando com IA...',
    process_list_title: 'Processo de Desembaraço — Lista de CE', process_list_desc: 'Clique em “Ver Processo” para rastrear',
    search_placeholder: 'Buscar CE ou carga...', filter: 'Filtrar',
    bl_number: 'Conhecimento de Embarque', goods_desc: 'Descrição da Carga', declaration_date: 'Data de Declaração', port_col: 'Porto', status_col: 'Status', action_col: 'Ação',
    view_process: 'Ver Processo', status_cleared: 'Liberado', status_processing: 'Em Processo', status_inspection: 'Em Inspeção',
    total_records: (n) => `${n} registros`, prev_page: 'Anterior', next_page: 'Próximo',
    back_to_list: 'Voltar à Lista', container_title: 'Status do Processo de Importação', bl_label: 'CE: ', export_progress: 'Exportar Progresso',
    overall_progress: 'Progresso Geral:', current_step_label: 'Etapa Atual:', all_done: 'Tudo Concluído ✓',
    edit_step_title: 'Editar Status da Etapa', step_name_label: 'Nome da Etapa', status_label: 'Status',
    completion_time_label: 'Data de Conclusão', completion_time_hint: '(opcional, ex.: 08-24 08:10)', completion_time_ph: 'Inserir data...',
    step_desc_label: 'Descrição da Etapa', cancel: 'Cancelar', save_update: 'Salvar', save_success: 'Salvo!',
    goods1: 'Peças de Maquinário', goods2: 'Eletrônicos', goods3: 'Matérias-Primas Têxteis', goods4: 'Equipamentos Médicos', goods5: 'Autopecas',
    cost_structure_title: 'Estrutura de Custos (Este Mês)', total_import_cost: 'Custo Total de Importação', largest_share: 'Maior Participação', major_tax_details: 'Principais Tributos',
    customs_fees_section: 'Taxas Aduaneiras', total_customs_fee: 'Taxa Aduaneira Total (BRL)', refund_fee: 'Taxa de Reembolso (BRL)',
    product_info_section: 'Informações do Produto', add_product: 'Adicionar Produto', product_name_ph: 'Nome do Produto', qty_ph: 'Quantidade',
    additional_fees_section: 'Taxas Adicionais', usd_amount: 'Valor em USD', usd_rate_label: 'Taxa USD (1 USD = ? BRL)',
    refresh_rate: 'Atualizar', fetching_rate: 'Buscando...', realtime_tag: 'Ao vivo', manual_tag: 'Manual',
    other_fees_label: 'Outras Taxas (BRL)', auto_fetching_ph: 'Buscando taxa...', updated_at: 'Atualizado em ',
    calculate_cost: 'Calcular Custo', fill_data_prompt: 'Preencha os dados à esquerda', click_calc_prompt: 'Clique em “Calcular Custo” para ver os resultados',
    cost_summary: 'Resumo de Custos', container_total_cost: 'Custo Total do Contêiner', per_item_cost: 'Custo por Unidade',
    formula_title: 'Fórmula de Cálculo', formula_text: 'Custo por item = (Taxa Total − Reembolso + Equiv. USD + Outras Taxas) ÷ Quantidade Total',
    cost_breakdown: 'Detalhamento de Custos', customs_fee_row: 'Taxa Aduaneira Total', refund_fee_row: 'Taxa de Reembolso', net_customs_row: 'Taxa Líquida',
    exchange_rate_row: 'Taxa de Câmbio USD', usd_converted_row: 'Equiv. USD (BRL)', other_fees_row: 'Outras Taxas', total_cost_base_row: 'Base de Custo Total',
    product_cost_detail: 'Detalhamento por Produto', qty_label_detail: 'Qtd: ', pcs: 'un.', per_unit: 'BRL/un.',
    reset: 'Redefinir', export_pdf: 'Exportar PDF', unnamed_product: 'Produto Sem Nome',
    rate_parse_failed: 'Falha ao analisar taxa', rate_network_failed: 'Erro de rede, insira manualmente',
    recent_records_title: 'Registros Recentes', details: 'Detalhes', afrmm: 'AFRMM e Outros',
    fetching_in: 'Buscando',
  },
};

const LanguageContext = createContext('zh');
const useT = () => {
  const lang = useContext(LanguageContext);
  return TRANSLATIONS[lang] || TRANSLATIONS.zh;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5001';
const AUTH_STORAGE_KEY = 'portabrasil_auth';

const readStoredAuth = () => {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem(AUTH_STORAGE_KEY) || sessionStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (parsed && parsed.access_token) {
      return parsed;
    }
    return null;
  } catch (error) {
    return null;
  }
};

const persistAuth = (authPayload, remember = true) => {
  if (typeof window === 'undefined') return;
  const serialized = JSON.stringify(authPayload);
  if (remember) {
    localStorage.setItem(AUTH_STORAGE_KEY, serialized);
    sessionStorage.removeItem(AUTH_STORAGE_KEY);
  } else {
    sessionStorage.setItem(AUTH_STORAGE_KEY, serialized);
    localStorage.removeItem(AUTH_STORAGE_KEY);
  }
};

const clearAuthStorage = () => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(AUTH_STORAGE_KEY);
  sessionStorage.removeItem(AUTH_STORAGE_KEY);
};

const buildAuthHeaders = (token, headers = {}) => ({
  ...headers,
  Authorization: `Bearer ${token}`,
});

const fetchJSON = async (url, options = {}) => {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data?.error || `Request failed: ${response.status}`);
  }
  return data;
};

const formatCurrencyBRL = (value) => {
  const number = Number(value || 0);
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(number);
};

const formatFileSize = (bytes) => {
  const size = Number(bytes || 0);
  if (size <= 0) return '0 B';
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
};

// --- 数据模型 & 共享组件 ---

const SidebarItem = ({ icon: Icon, label, isActive, onClick }) => {
  return (
    <div 
      onClick={onClick}
      className={`flex items-center px-6 py-4 cursor-pointer transition-colors duration-200 ${
        isActive 
          ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-500' 
          : 'text-gray-600 hover:bg-gray-50 border-l-4 border-transparent'
      }`}
    >
      <Icon className="w-5 h-5 mr-3" />
      <span className="font-medium text-sm">{label}</span>
    </div>
  );
};

// --- 页面视图组件 ---

// 1. 首页视图
const HomeView = ({ authToken }) => {
  const t = useT();
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
};

// 2. 文档上传视图
const UploadView = ({ authToken }) => {
  const t = useT();
  const fileInputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const loadFiles = async () => {
    if (!authToken) return;
    setLoading(true);
    setError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/files?limit=20`, {
        headers: buildAuthHeaders(authToken),
      });
      setFiles(data?.items || []);
    } catch (err) {
      setError(err.message || 'failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, [authToken]);

  const handlePickFile = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  const handleFileChange = async (event) => {
    const selected = event.target.files?.[0];
    if (!selected || !authToken) return;
    const formData = new FormData();
    formData.append('file', selected);
    formData.append('parse', 'true');
    setUploading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/files/upload`, {
        method: 'POST',
        headers: buildAuthHeaders(authToken),
        body: formData,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data?.error || 'Upload failed');
      }
      await loadFiles();
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      event.target.value = '';
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
      <h2 className="text-xl font-bold text-gray-800 mb-6">{t.upload_title}</h2>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleFileChange}
      />

      <div className="border-2 border-dashed border-gray-300 rounded-2xl bg-gray-50 p-12 text-center hover:bg-blue-50 hover:border-blue-400 transition-colors cursor-pointer mb-8" onClick={handlePickFile}>
        <div className="bg-white w-16 h-16 rounded-full shadow-sm flex items-center justify-center mx-auto mb-4">
          <UploadCloud className="w-8 h-8 text-blue-500" />
        </div>
        <h3 className="text-lg font-medium text-gray-800 mb-2">{t.upload_drag}</h3>
        <p className="text-sm text-gray-500 mb-4">{t.upload_formats}</p>
        <button type="button" className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50">
          {uploading ? t.fetching_rate : t.browse}
        </button>
      </div>

      <div>
        <h3 className="text-base font-semibold text-gray-800 mb-4">{t.recent_uploads}</h3>
        <div className="space-y-3">
          {loading ? <div className="text-sm text-gray-500">{t.fetching_rate}</div> : null}
          {!loading && files.length === 0 ? <div className="text-sm text-gray-400">No files yet.</div> : null}
          {files.map((file, i) => {
            const parseStatus = String(file.parse_status || '').toUpperCase();
            const done = parseStatus === 'SUCCESS';
            return (
              <div key={file.id || i} className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:shadow-sm transition-shadow">
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <FileText className="w-6 h-6 text-blue-500" />
                  </div>
                  <div>
                    <div className="font-medium text-sm text-gray-800">{file.file_name}</div>
                    <div className="text-xs text-gray-500">{formatFileSize(file.file_size)} • {file.upload_time}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  {done ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {t.verified}
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      {t.ai_processing}
                    </span>
                  )}
                  <button className="text-gray-400 hover:text-gray-600">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
        {error ? <p className="text-xs text-amber-600 mt-3">{error}</p> : null}
      </div>
    </div>
  );
};

// 3. 流程跟踪视图 (原设计核心)
const ProcessTrackingView = ({ authToken }) => {
  const t = useT();
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


// 4. 成本分析视图
const CostAnalysisView = ({ authToken }) => {
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
};

// 5. 报表分析视图
const ReportView = ({ authToken }) => {
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


// --- 主应用入口 ---

export default function App() {
  const [activeMenu, setActiveMenu] = useState('home');
  const [lang, setLang] = useState('zh');
  const [auth, setAuth] = useState(() => readStoredAuth());
  const t = TRANSLATIONS[lang] || TRANSLATIONS.zh;
  const langs = ['zh', 'en', 'pt'];
  const langLabels = { zh: '中文', en: 'EN', pt: 'PT' };
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
    { key: 'home',    label: t.nav_home,    icon: Home },
    { key: 'upload',  label: t.nav_upload,  icon: UploadCloud },
    { key: 'process', label: t.nav_process, icon: MapIcon },
    { key: 'cost',    label: t.nav_cost,    icon: PieChart },
    { key: 'report',  label: t.nav_report,  icon: BarChart2 },
  ];

  const renderContent = () => {
    switch (activeMenu) {
      case 'home':    return <HomeView authToken={auth?.access_token} />;
      case 'upload':  return <UploadView authToken={auth?.access_token} />;
      case 'process': return <ProcessTrackingView authToken={auth?.access_token} />;
      case 'cost':    return <CostAnalysisView authToken={auth?.access_token} />;
      case 'report':  return <ReportView authToken={auth?.access_token} />;
      default:        return <HomeView authToken={auth?.access_token} />;
    }
  };

  const activeLabel = menuItems.find(m => m.key === activeMenu)?.label || '';

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} lang={lang} onLangChange={setLang} />;
  }

  return (
    <LanguageContext.Provider value={lang}>
    <div className="flex h-screen bg-[#f4f7f9] font-sans">
      {/* Sidebar */}
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
        
        {/* 底部帮助支持入口 */}
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

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8 shadow-sm z-0 shrink-0">
          <div className="flex items-center text-gray-500 text-sm">
            <span className="hover:text-gray-800 cursor-pointer">{t.system}</span>
            <ChevronRight className="w-4 h-4 mx-2" />
            <span className="font-medium text-gray-800">{activeLabel}</span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative hidden md:block">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input type="text" placeholder={t.globalSearch} className="pl-9 pr-4 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-100 w-48 transition-all focus:w-64" />
            </div>
            {/* 语言切换按钮 */}
            <button
              onClick={() => setLang(l => { const i = langs.indexOf(l); return langs[(i + 1) % 3]; })}
              className="flex items-center space-x-1 text-gray-500 hover:text-blue-600 px-2.5 py-1 rounded-lg hover:bg-blue-50 transition-colors border border-gray-200"
            >
              <Globe className="w-4 h-4" />
              <span className="text-xs font-semibold">{langLabels[lang]}</span>
            </button>
            <button className="text-gray-400 hover:text-gray-600 transition-colors relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
            </button>
            <button onClick={handleLogout} className="flex items-center space-x-1 text-gray-400 hover:text-red-500 px-2.5 py-1 rounded-lg hover:bg-red-50 transition-colors border border-gray-200">
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

        {/* Dashboard Content */}
        <main className="flex-1 overflow-auto p-8">
          <div className="max-w-[1400px] mx-auto">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
    </LanguageContext.Provider>
  );
}
