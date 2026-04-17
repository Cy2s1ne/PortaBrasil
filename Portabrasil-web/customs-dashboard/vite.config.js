import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
    server: {
    host: '0.0.0.0', // 允许外部 IP 访问
    port: 5173,      // 确保端口是 5173
    strictPort: true // 如果端口被占用直接报错，防止自动切换端口
  }
})
