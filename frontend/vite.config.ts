import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';

// Development: `npm run dev` serves the app on :5173 and sends /api to Flask (:5000), so the session cookie and the
// CSRF token work without any CORS setup. Build: the files go to app/static/app, which Flask serves (app/routes/spa_routes.py).
export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === 'build' ? '/static/app/' : '/',
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: { port: 5173, proxy: { '/api': 'http://127.0.0.1:5000' } },
  build: { outDir: '../app/static/app', emptyOutDir: true },
  test: { environment: 'node' },
}));
