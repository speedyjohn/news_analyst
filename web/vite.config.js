import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Куку с JWT ставит бэкенд, поэтому в dev ходим через прокси — иначе она не долетит.
    proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } },
  },
});
