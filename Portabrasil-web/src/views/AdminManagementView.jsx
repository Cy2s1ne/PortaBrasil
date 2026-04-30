import { useCallback, useEffect, useMemo, useState } from 'react';
import { KeyRound, Pencil, Plus, Search, ShieldCheck, ToggleLeft, ToggleRight, X } from 'lucide-react';
import { API_BASE_URL } from '../shared/config/api';
import { useT } from '../shared/i18n/language-context';
import { buildAuthHeaders, fetchJSON } from '../shared/utils/http';
import { useAuth } from '../shared/auth/AuthContext';

const PAGE_SIZE = 10;
const EMPTY_FORM = {
  username: '',
  password: '',
  real_name: '',
  phone: '',
  email: '',
  status: 1,
  role_codes: [],
};

export default function AdminManagementView() {
  const { auth } = useAuth();
  const t = useT();
  const authToken = auth?.access_token;

  const [roles, setRoles] = useState([]);
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);

  const [searchInput, setSearchInput] = useState('');
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [page, setPage] = useState(1);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [actionBusyId, setActionBusyId] = useState(null);

  const [modalMode, setModalMode] = useState(null);
  const [editingUser, setEditingUser] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formBusy, setFormBusy] = useState(false);
  const [formError, setFormError] = useState('');

  const [passwordTarget, setPasswordTarget] = useState(null);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordBusy, setPasswordBusy] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const roleMap = useMemo(() => {
    const map = new Map();
    roles.forEach((role) => map.set(role.role_code, role.role_name || role.role_code));
    return map;
  }, [roles]);

  const loadRoles = useCallback(async () => {
    if (!authToken) return;
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/admin/roles`, {
        headers: buildAuthHeaders(authToken),
      });
      setRoles(data?.items || []);
    } catch (err) {
      setError(err.message || 'failed');
    }
  }, [authToken]);

  const loadUsers = useCallback(async () => {
    if (!authToken) return;
    const params = new URLSearchParams({
      limit: String(PAGE_SIZE),
      offset: String((page - 1) * PAGE_SIZE),
    });
    if (query.trim()) params.set('q', query.trim());
    if (statusFilter !== '') params.set('status', statusFilter);
    if (roleFilter) params.set('role_code', roleFilter);

    setLoading(true);
    setError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/admin/users?${params.toString()}`, {
        headers: buildAuthHeaders(authToken),
      });
      setRows(data?.items || []);
      setTotal(Number(data?.total || 0));
    } catch (err) {
      setError(err.message || 'failed');
    } finally {
      setLoading(false);
    }
  }, [authToken, page, query, statusFilter, roleFilter]);

  useEffect(() => {
    loadRoles();
  }, [loadRoles]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const openCreateModal = () => {
    setModalMode('create');
    setEditingUser(null);
    setForm({
      ...EMPTY_FORM,
      role_codes: roles.length ? [roles[0].role_code] : [],
    });
    setFormError('');
  };

  const openEditModal = (row) => {
    setModalMode('edit');
    setEditingUser(row);
    setForm({
      username: row.username || '',
      password: '',
      real_name: row.real_name || '',
      phone: row.phone || '',
      email: row.email || '',
      status: Number(row.status || 0),
      role_codes: row.roles || [],
    });
    setFormError('');
  };

  const closeFormModal = () => {
    setModalMode(null);
    setEditingUser(null);
    setForm(EMPTY_FORM);
    setFormError('');
  };

  const toggleRole = (roleCode) => {
    setForm((prev) => {
      const exists = prev.role_codes.includes(roleCode);
      if (exists) {
        return { ...prev, role_codes: prev.role_codes.filter((code) => code !== roleCode) };
      }
      return { ...prev, role_codes: [...prev.role_codes, roleCode] };
    });
  };

  const submitForm = async () => {
    if (!authToken || !modalMode || formBusy) return;
    if (!form.username.trim()) {
      setFormError(t.admin_user_required);
      return;
    }
    if (modalMode === 'create' && form.password.length < 6) {
      setFormError(t.admin_password_min);
      return;
    }
    if (!form.role_codes.length) {
      setFormError(t.admin_role_required);
      return;
    }

    const payload = {
      username: form.username.trim(),
      real_name: form.real_name.trim(),
      phone: form.phone.trim(),
      email: form.email.trim(),
      status: Number(form.status || 0),
      role_codes: form.role_codes,
    };
    if (modalMode === 'create') payload.password = form.password;

    setFormBusy(true);
    setFormError('');
    try {
      if (modalMode === 'create') {
        await fetchJSON(`${API_BASE_URL}/api/admin/users`, {
          method: 'POST',
          headers: buildAuthHeaders(authToken, { 'Content-Type': 'application/json' }),
          body: JSON.stringify(payload),
        });
        setMessage(t.admin_create_success);
      } else {
        await fetchJSON(`${API_BASE_URL}/api/admin/users/${editingUser.id}`, {
          method: 'PUT',
          headers: buildAuthHeaders(authToken, { 'Content-Type': 'application/json' }),
          body: JSON.stringify(payload),
        });
        setMessage(t.admin_update_success);
      }
      closeFormModal();
      loadUsers();
    } catch (err) {
      setFormError(err.message || 'failed');
    } finally {
      setFormBusy(false);
    }
  };

  const toggleUserStatus = async (row) => {
    if (!authToken || actionBusyId) return;
    const nextStatus = Number(row.status || 0) === 1 ? 0 : 1;
    setActionBusyId(row.id);
    setError('');
    try {
      await fetchJSON(`${API_BASE_URL}/api/admin/users/${row.id}/status`, {
        method: 'PUT',
        headers: buildAuthHeaders(authToken, { 'Content-Type': 'application/json' }),
        body: JSON.stringify({ status: nextStatus }),
      });
      setMessage(nextStatus === 1 ? t.admin_enable_success : t.admin_disable_success);
      loadUsers();
    } catch (err) {
      setError(err.message || 'failed');
    } finally {
      setActionBusyId(null);
    }
  };

  const openPasswordModal = (row) => {
    setPasswordTarget(row);
    setNewPassword('');
    setConfirmPassword('');
    setPasswordError('');
  };

  const closePasswordModal = () => {
    setPasswordTarget(null);
    setNewPassword('');
    setConfirmPassword('');
    setPasswordError('');
  };

  const submitPasswordReset = async () => {
    if (!authToken || !passwordTarget || passwordBusy) return;
    if (newPassword.length < 6) {
      setPasswordError(t.admin_password_min);
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError(t.admin_password_mismatch);
      return;
    }

    setPasswordBusy(true);
    setPasswordError('');
    try {
      await fetchJSON(`${API_BASE_URL}/api/admin/users/${passwordTarget.id}/password`, {
        method: 'PUT',
        headers: buildAuthHeaders(authToken, { 'Content-Type': 'application/json' }),
        body: JSON.stringify({ new_password: newPassword }),
      });
      setMessage(t.admin_reset_success);
      closePasswordModal();
    } catch (err) {
      setPasswordError(err.message || 'failed');
    } finally {
      setPasswordBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-800">{t.admin_title}</h2>
            <p className="text-xs text-gray-400 mt-0.5">{t.admin_desc}</p>
          </div>
          <button
            onClick={openCreateModal}
            className="inline-flex items-center px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            {t.admin_create}
          </button>
        </div>

        <div className="px-6 py-4 border-b border-gray-100 flex flex-wrap gap-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  setPage(1);
                  setQuery(searchInput);
                }
              }}
              placeholder={t.admin_search_ph}
              className="pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 w-72"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => {
              setPage(1);
              setStatusFilter(e.target.value);
            }}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="">{t.admin_status_all}</option>
            <option value="1">{t.admin_status_enabled}</option>
            <option value="0">{t.admin_status_disabled}</option>
          </select>
          <select
            value={roleFilter}
            onChange={(e) => {
              setPage(1);
              setRoleFilter(e.target.value);
            }}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="">{t.admin_role_all}</option>
            {roles.map((role) => (
              <option key={role.id} value={role.role_code}>{role.role_name}</option>
            ))}
          </select>
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

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500">
            <thead className="text-xs text-gray-700 uppercase bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-4 font-semibold">{t.admin_col_username}</th>
                <th className="px-6 py-4 font-semibold">{t.admin_col_name}</th>
                <th className="px-6 py-4 font-semibold">{t.admin_col_email}</th>
                <th className="px-6 py-4 font-semibold">{t.admin_col_phone}</th>
                <th className="px-6 py-4 font-semibold">{t.admin_col_roles}</th>
                <th className="px-6 py-4 font-semibold">{t.admin_col_status}</th>
                <th className="px-6 py-4 font-semibold">{t.admin_col_created}</th>
                <th className="px-6 py-4 font-semibold text-right">{t.action_col}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td className="px-6 py-6 text-sm text-gray-500" colSpan={8}>{t.fetching_rate}</td></tr>
              ) : rows.length === 0 ? (
                <tr><td className="px-6 py-6 text-sm text-gray-400" colSpan={8}>{t.admin_empty}</td></tr>
              ) : rows.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900">{row.username}</td>
                  <td className="px-6 py-4">{row.real_name || '-'}</td>
                  <td className="px-6 py-4">{row.email || '-'}</td>
                  <td className="px-6 py-4">{row.phone || '-'}</td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1.5">
                      {(row.roles || []).map((roleCode) => (
                        <span key={roleCode} className="inline-flex items-center px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-xs font-medium">
                          <ShieldCheck className="w-3 h-3 mr-1" />
                          {roleMap.get(roleCode) || roleCode}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {Number(row.status || 0) === 1 ? (
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">{t.admin_status_enabled}</span>
                    ) : (
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">{t.admin_status_disabled}</span>
                    )}
                  </td>
                  <td className="px-6 py-4">{row.created_at || '-'}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end gap-1.5">
                      <button
                        onClick={() => openEditModal(row)}
                        className="inline-flex items-center px-2.5 py-1.5 rounded-md border border-gray-200 text-gray-600 hover:bg-gray-50 text-xs font-medium"
                      >
                        <Pencil className="w-3.5 h-3.5 mr-1" />
                        {t.admin_edit}
                      </button>
                      <button
                        onClick={() => toggleUserStatus(row)}
                        disabled={actionBusyId === row.id}
                        className="inline-flex items-center px-2.5 py-1.5 rounded-md border border-gray-200 text-gray-600 hover:bg-gray-50 text-xs font-medium disabled:opacity-40"
                      >
                        {Number(row.status || 0) === 1 ? (
                          <ToggleLeft className="w-3.5 h-3.5 mr-1 text-amber-500" />
                        ) : (
                          <ToggleRight className="w-3.5 h-3.5 mr-1 text-green-500" />
                        )}
                        {Number(row.status || 0) === 1 ? t.admin_disable : t.admin_enable}
                      </button>
                      <button
                        onClick={() => openPasswordModal(row)}
                        className="inline-flex items-center px-2.5 py-1.5 rounded-md border border-gray-200 text-gray-600 hover:bg-gray-50 text-xs font-medium"
                      >
                        <KeyRound className="w-3.5 h-3.5 mr-1" />
                        {t.admin_reset_pwd}
                      </button>
                    </div>
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
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-40"
            >
              {t.prev_page}
            </button>
            <button className="px-3 py-1 bg-blue-50 text-blue-600 border border-blue-200 rounded">{page}</button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-40"
            >
              {t.next_page}
            </button>
          </div>
        </div>
      </div>

      {message ? (
        <div className="px-4 py-3 border border-green-200 bg-green-50 rounded-lg text-sm text-green-700">{message}</div>
      ) : null}
      {error ? (
        <div className="px-4 py-3 border border-amber-200 bg-amber-50 rounded-lg text-sm text-amber-700">{error}</div>
      ) : null}

      {modalMode ? (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="w-[640px] max-w-[95vw] bg-white rounded-2xl shadow-2xl p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-800">{modalMode === 'create' ? t.admin_create : t.admin_edit}</h3>
              <button onClick={closeFormModal} className="p-1 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1.5">{t.admin_col_username}</label>
                <input
                  value={form.username}
                  onChange={(e) => setForm((prev) => ({ ...prev, username: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  placeholder={t.admin_col_username}
                />
              </div>
              {modalMode === 'create' ? (
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1.5">{t.passwordLabel || 'Password'}</label>
                  <input
                    type="password"
                    value={form.password}
                    onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    placeholder={t.admin_password_ph}
                  />
                </div>
              ) : null}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1.5">{t.admin_col_name}</label>
                <input
                  value={form.real_name}
                  onChange={(e) => setForm((prev) => ({ ...prev, real_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1.5">{t.admin_col_phone}</label>
                <input
                  value={form.phone}
                  onChange={(e) => setForm((prev) => ({ ...prev, phone: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1.5">{t.admin_col_email}</label>
                <input
                  value={form.email}
                  onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1.5">{t.admin_col_status}</label>
                <select
                  value={String(form.status)}
                  onChange={(e) => setForm((prev) => ({ ...prev, status: Number(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                  <option value="1">{t.admin_status_enabled}</option>
                  <option value="0">{t.admin_status_disabled}</option>
                </select>
              </div>
            </div>

            <div className="mt-5">
              <label className="block text-xs font-medium text-gray-500 mb-2">{t.admin_col_roles}</label>
              <div className="flex flex-wrap gap-2">
                {roles.map((role) => {
                  const checked = form.role_codes.includes(role.role_code);
                  return (
                    <button
                      key={role.id}
                      type="button"
                      onClick={() => toggleRole(role.role_code)}
                      className={`px-3 py-1.5 rounded-full border text-xs font-medium transition-colors ${
                        checked
                          ? 'border-blue-300 bg-blue-50 text-blue-700'
                          : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {role.role_name}
                    </button>
                  );
                })}
              </div>
            </div>

            {formError ? <p className="mt-4 text-xs text-amber-600">{formError}</p> : null}
            <div className="mt-6 flex justify-end gap-2">
              <button onClick={closeFormModal} className="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
                {t.cancel}
              </button>
              <button
                onClick={submitForm}
                disabled={formBusy}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-60"
              >
                {formBusy ? t.fetching_rate : t.save_update}
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {passwordTarget ? (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="w-[460px] max-w-[95vw] bg-white rounded-2xl shadow-2xl p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-800">{t.admin_reset_pwd}</h3>
              <button onClick={closePasswordModal} className="p-1 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-sm text-gray-500 mb-4">{t.admin_reset_target}{passwordTarget.username}</p>
            <div className="space-y-3">
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder={t.admin_password_ph}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder={t.admin_password_confirm_ph}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {passwordError ? <p className="mt-4 text-xs text-amber-600">{passwordError}</p> : null}
            <div className="mt-6 flex justify-end gap-2">
              <button onClick={closePasswordModal} className="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
                {t.cancel}
              </button>
              <button
                onClick={submitPasswordReset}
                disabled={passwordBusy}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-60"
              >
                {passwordBusy ? t.fetching_rate : t.admin_reset_confirm}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
