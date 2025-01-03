import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 8080,
    host: true,
    strictPort: true,
    cors: true,
    allowedHosts: [
      '0.0.0.0',
      'localhost',
      '127.0.0.1',
      'admin.ext4.cn'
    ]
  }
})
