import { useState } from "react";
import { Eye, EyeOff, Anchor, Globe2 } from "lucide-react";
import { AnimatedCharacters } from "./animated-characters";
import { InteractiveHoverButton } from "./interactive-hover-button";

export default function LoginPage({ onLogin }) {
  const [showPassword, setShowPassword] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const passwordLength = password.length;

  const onSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    await new Promise((r) => setTimeout(r, 1200));
    setIsLoading(false);
    onLogin();
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
          <a href="#" className="hover:text-white/70 transition-colors">Política de Privacidade</a>
          <a href="#" className="hover:text-white/70 transition-colors">Termos de Serviço</a>
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
            {/* Header */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-slate-900 mb-1">Bem-vindo de volta!</h2>
              <p className="text-sm text-slate-500">Por favor, insira seus dados para continuar</p>
            </div>

            {/* Form */}
            <form onSubmit={onSubmit} className="space-y-5">
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  E-mail
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onFocus={() => setIsTyping(true)}
                  onBlur={() => setIsTyping(false)}
                  placeholder="seu@email.com.br"
                  required
                  className="w-full h-12 px-4 bg-white border border-slate-300 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Senha
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
                  <input type="checkbox" className="w-4 h-4 rounded border-slate-300 accent-blue-600 cursor-pointer" />
                  <span className="text-sm text-slate-500">Lembrar por 30 dias</span>
                </label>
                <a href="#" className="text-sm text-blue-600 hover:underline font-medium">Esqueceu a senha?</a>
              </div>

              {/* Submit */}
              <InteractiveHoverButton
                type="submit"
                text="Entrar"
                disabled={isLoading}
                className="w-full"
              />
            </form>

            {/* Divider */}
            <div className="flex items-center my-6">
              <div className="flex-1 h-px bg-slate-200" />
              <span className="px-4 text-xs text-slate-400 font-medium">ou</span>
              <div className="flex-1 h-px bg-slate-200" />
            </div>

            {/* Google sign-in */}
            <button
              type="button"
              onClick={onSubmit}
              className="w-full h-12 flex items-center justify-center gap-3 rounded-full border-2 border-slate-200 bg-white hover:bg-slate-50 hover:border-slate-300 text-slate-700 font-medium text-sm transition-all"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              Entrar com Google
            </button>

            {/* Sign up link */}
            <p className="text-center text-sm text-slate-500 mt-6">
              Não tem uma conta?{" "}
              <a href="#" className="text-blue-600 font-semibold hover:underline">Criar Conta</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}