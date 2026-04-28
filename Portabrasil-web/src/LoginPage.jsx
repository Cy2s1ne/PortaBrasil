import { useState } from "react";
import { Eye, EyeOff, Anchor, Globe2 } from "lucide-react";
import { AnimatedCharacters } from "./animated-characters";
import { InteractiveHoverButton } from "./interactive-hover-button";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5001";
const LANGS = ["zh", "en", "pt"];
const LANG_LABELS = { zh: "中文", en: "EN", pt: "PT" };

const LOGIN_I18N = {
  zh: {
    welcomeTitle: "欢迎回来！",
    welcomeDesc: "请输入账号和密码登录系统",
    accountLabel: "账号 / 邮箱",
    accountPlaceholder: "用户名或邮箱",
    passwordLabel: "密码",
    rememberLogin: "记住登录",
    forgotPassword: "忘记密码？",
    loginButton: "登录",
    loginLoading: "登录中...",
    loginRequired: "请输入账号和密码",
    loginFailed: "登录失败，请检查账号和密码",
    loginRetry: "登录失败，请稍后再试",
    resetTitle: "重置密码",
    resetRequired: "请填写用户名、邮箱和新密码",
    resetLength: "新密码至少 6 位",
    resetMismatch: "两次输入的新密码不一致",
    resetFailed: "重置密码失败",
    resetHint: "密码已重置，请使用新密码登录",
    resetUsernamePh: "用户名",
    resetEmailPh: "注册邮箱",
    resetNewPasswordPh: "新密码",
    resetConfirmPh: "确认新密码",
    resetSubmitting: "提交中...",
    resetButton: "重置密码",
    privacy: "隐私政策",
    terms: "服务条款",
    langButton: "语言",
  },
  en: {
    welcomeTitle: "Welcome Back!",
    welcomeDesc: "Please sign in with your account and password",
    accountLabel: "Account / E-mail",
    accountPlaceholder: "Username or e-mail",
    passwordLabel: "Password",
    rememberLogin: "Remember me",
    forgotPassword: "Forgot password?",
    loginButton: "Sign in",
    loginLoading: "Signing in...",
    loginRequired: "Please enter account and password",
    loginFailed: "Login failed. Please check your account and password",
    loginRetry: "Login failed. Please try again later",
    resetTitle: "Reset Password",
    resetRequired: "Please fill username, e-mail and new password",
    resetLength: "New password must be at least 6 characters",
    resetMismatch: "The two passwords do not match",
    resetFailed: "Password reset failed",
    resetHint: "Password reset complete. Please sign in with the new password",
    resetUsernamePh: "Username",
    resetEmailPh: "Registered e-mail",
    resetNewPasswordPh: "New password",
    resetConfirmPh: "Confirm new password",
    resetSubmitting: "Submitting...",
    resetButton: "Reset password",
    privacy: "Privacy Policy",
    terms: "Terms of Service",
    langButton: "Language",
  },
  pt: {
    welcomeTitle: "Bem-vindo de volta!",
    welcomeDesc: "Insira sua conta e senha para continuar",
    accountLabel: "Conta / E-mail",
    accountPlaceholder: "Usuário ou e-mail",
    passwordLabel: "Senha",
    rememberLogin: "Lembrar login",
    forgotPassword: "Esqueceu a senha?",
    loginButton: "Entrar",
    loginLoading: "Entrando...",
    loginRequired: "Informe conta e senha",
    loginFailed: "Falha no login. Verifique conta e senha",
    loginRetry: "Falha no login. Tente novamente mais tarde",
    resetTitle: "Redefinir senha",
    resetRequired: "Preencha usuário, e-mail e nova senha",
    resetLength: "A nova senha deve ter pelo menos 6 caracteres",
    resetMismatch: "As senhas não coincidem",
    resetFailed: "Falha ao redefinir senha",
    resetHint: "Senha redefinida. Faça login com a nova senha",
    resetUsernamePh: "Usuário",
    resetEmailPh: "E-mail cadastrado",
    resetNewPasswordPh: "Nova senha",
    resetConfirmPh: "Confirmar nova senha",
    resetSubmitting: "Enviando...",
    resetButton: "Redefinir senha",
    privacy: "Política de Privacidade",
    terms: "Termos de Serviço",
    langButton: "Idioma",
  },
};

export default function LoginPage({ onLogin, lang = "zh", onLangChange }) {
  const resolvedLang = LANGS.includes(lang) ? lang : "zh";
  const t = LOGIN_I18N[resolvedLang];

  const [showPassword, setShowPassword] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [infoMessage, setInfoMessage] = useState("");

  const [showForgotPanel, setShowForgotPanel] = useState(false);
  const [resetUsername, setResetUsername] = useState("");
  const [resetEmail, setResetEmail] = useState("");
  const [resetPassword, setResetPassword] = useState("");
  const [resetPasswordConfirm, setResetPasswordConfirm] = useState("");
  const [resetLoading, setResetLoading] = useState(false);
  const [resetError, setResetError] = useState("");
  const [resetInfo, setResetInfo] = useState("");

  const passwordLength = password.length;

  const toggleLanguage = () => {
    if (!onLangChange) return;
    const currentIndex = LANGS.indexOf(resolvedLang);
    const nextLang = LANGS[(currentIndex + 1) % LANGS.length];
    onLangChange(nextLang);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!account.trim() || !password) {
      setErrorMessage(t.loginRequired);
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    setInfoMessage("");

    try {
      const loginPayload = account.includes("@")
        ? { email: account.trim(), password }
        : { username: account.trim(), password };

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(loginPayload),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || t.loginFailed);
      }

      onLogin?.({
        access_token: data.access_token,
        user: data.user,
        remember: rememberMe,
      });
    } catch (error) {
      setErrorMessage(error.message || t.loginRetry);
    } finally {
      setIsLoading(false);
    }
  };

  const onForgotPassword = async (e) => {
    e.preventDefault();
    setResetError("");
    setResetInfo("");

    if (!resetUsername.trim() || !resetEmail.trim() || !resetPassword) {
      setResetError(t.resetRequired);
      return;
    }
    if (resetPassword.length < 6) {
      setResetError(t.resetLength);
      return;
    }
    if (resetPassword !== resetPasswordConfirm) {
      setResetError(t.resetMismatch);
      return;
    }

    setResetLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: resetUsername.trim(),
          email: resetEmail.trim(),
          new_password: resetPassword,
        }),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || t.resetFailed);
      }

      setResetInfo(data.message || t.resetHint);
      setInfoMessage(t.resetHint);
      setAccount(resetUsername.trim());
      setPassword("");
      setResetPassword("");
      setResetPasswordConfirm("");
      setShowForgotPanel(false);
    } catch (error) {
      setResetError(error.message || t.resetFailed);
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* ─── LEFT: half viewport (no max-width cap) + characters vertically centered ─── */}
      <div
        className="hidden lg:flex relative overflow-hidden shrink-0 w-[50%] xl:w-[52%] min-w-[420px]"
        style={{ background: "linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%)" }}
      >

        {/* Background map pattern overlay */}
        <div className="absolute inset-0 w-full h-full opacity-5"
          style={{
            backgroundImage: "url('https://www.transparenttextures.com/patterns/cartographer.png')",
            backgroundSize: "cover",
            backgroundPosition: "center",
          }} />

        {/* Decorative grid lines */}
        <div className="absolute inset-0 opacity-[0.05]"
          style={{
            backgroundImage: "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)",
            backgroundSize: "60px 60px",
          }} />

        {/* Brand header */}
        <div className="absolute top-10 left-10 z-20 flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
            <Anchor className="w-6 h-6 text-white" />
          </div>
          <span className="text-white font-bold text-xl tracking-tight">PortaBrasil</span>
        </div>

        {/* Characters: true vertical center in the panel (below header breathing room) */}
        <div className="absolute inset-0 pt-24 pb-28 pointer-events-none flex items-center justify-center">
          <div className="relative w-full max-w-[min(92%,480px)] h-[min(72vh,520px)] min-h-[300px]">
            <AnimatedCharacters
              isTyping={isTyping}
              showPassword={showPassword}
              passwordLength={passwordLength}
            />
          </div>
        </div>

        {/* Decorative elements - stylized waves */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-blue-900/20 to-transparent"></div>
        <div className="absolute top-32 right-12 opacity-30">
          <Globe2 className="w-8 h-8 text-cyan-300 animate-pulse" />
        </div>
        <div className="absolute bottom-40 left-16 opacity-20">
          <Globe2 className="w-5 h-5 text-blue-300 animate-pulse" style={{ animationDelay: "1s" }} />
        </div>

        {/* Footer links */}
        <div className="absolute bottom-8 left-0 right-0 flex justify-center gap-6 text-xs text-white/40 z-20">
          <a href="#" className="hover:text-white/70 transition-colors">{t.privacy}</a>
          <a href="#" className="hover:text-white/70 transition-colors">{t.terms}</a>
        </div>

        {/* Brand watermark */}
        <div className="absolute bottom-4 left-0 right-0 text-center">
          <span className="text-white/[0.03] text-6xl font-black tracking-widest select-none">PortaBrasil</span>
        </div>
      </div>

      {/* ─── RIGHT: Login Form (narrower card, rest is whitespace) ─── */}
      <div className="flex-1 flex items-center justify-center px-6 sm:px-10 py-12 bg-slate-50 min-w-0">
        <div className="w-full max-w-[22rem] sm:max-w-sm">

          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
            <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
              <Anchor className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-slate-900 tracking-tight">PortaBrasil</span>
          </div>

          <div className="rounded-3xl border border-slate-200/80 bg-white p-8 shadow-xl shadow-slate-200/50">
            <div className="mb-6 flex items-start justify-between gap-3">
              <div>
                <h2 className="text-2xl font-bold text-slate-900 mb-1">{t.welcomeTitle}</h2>
                <p className="text-sm text-slate-500">{t.welcomeDesc}</p>
              </div>
              <button
                type="button"
                onClick={toggleLanguage}
                className="shrink-0 inline-flex items-center gap-1 rounded-full border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
              >
                <Globe2 className="w-3.5 h-3.5" />
                {t.langButton}: {LANG_LABELS[resolvedLang]}
              </button>
            </div>

            {errorMessage ? (
              <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {errorMessage}
              </div>
            ) : null}

            {infoMessage ? (
              <div className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
                {infoMessage}
              </div>
            ) : null}

            {/* Form */}
            <form onSubmit={onSubmit} className="space-y-5">
              {/* Account */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  {t.accountLabel}
                </label>
                <input
                  type="text"
                  value={account}
                  onChange={(e) => setAccount(e.target.value)}
                  onFocus={() => setIsTyping(true)}
                  onBlur={() => setIsTyping(false)}
                  placeholder={t.accountPlaceholder}
                  required
                  className="w-full h-12 px-4 bg-white border border-slate-300 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  {t.passwordLabel}
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={() => setIsTyping(true)}
                    onBlur={() => setIsTyping(false)}
                    placeholder="••••••••"
                    required
                    className="w-full h-12 px-4 pr-12 bg-white border border-slate-300 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    {showPassword
                      ? <EyeOff className="w-4 h-4" />
                      : <Eye className="w-4 h-4" />
                    }
                  </button>
                </div>
              </div>

              {/* Remember + Forgot */}
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-300 accent-blue-600 cursor-pointer"
                  />
                  <span className="text-sm text-slate-500">{t.rememberLogin}</span>
                </label>
                <button
                  type="button"
                  onClick={() => {
                    setResetError("");
                    setResetInfo("");
                    setShowForgotPanel((prev) => !prev);
                  }}
                  className="text-sm text-blue-600 hover:underline font-medium"
                >
                  {t.forgotPassword}
                </button>
              </div>

              {/* Submit */}
              <InteractiveHoverButton
                type="submit"
                text={isLoading ? t.loginLoading : t.loginButton}
                disabled={isLoading}
                className="w-full"
              />
            </form>

            {showForgotPanel ? (
              <form onSubmit={onForgotPassword} className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4 space-y-3">
                <div className="text-sm font-semibold text-slate-700">{t.resetTitle}</div>

                {resetError ? (
                  <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                    {resetError}
                  </div>
                ) : null}

                {resetInfo ? (
                  <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
                    {resetInfo}
                  </div>
                ) : null}

                <input
                  type="text"
                  value={resetUsername}
                  onChange={(e) => setResetUsername(e.target.value)}
                  placeholder={t.resetUsernamePh}
                  required
                  className="w-full h-10 px-3 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                />
                <input
                  type="email"
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                  placeholder={t.resetEmailPh}
                  required
                  className="w-full h-10 px-3 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                />
                <input
                  type="password"
                  value={resetPassword}
                  onChange={(e) => setResetPassword(e.target.value)}
                  placeholder={t.resetNewPasswordPh}
                  required
                  className="w-full h-10 px-3 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                />
                <input
                  type="password"
                  value={resetPasswordConfirm}
                  onChange={(e) => setResetPasswordConfirm(e.target.value)}
                  placeholder={t.resetConfirmPh}
                  required
                  className="w-full h-10 px-3 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                />

                <button
                  type="submit"
                  disabled={resetLoading}
                  className="w-full h-10 rounded-lg bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
                >
                  {resetLoading ? t.resetSubmitting : t.resetButton}
                </button>
              </form>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
