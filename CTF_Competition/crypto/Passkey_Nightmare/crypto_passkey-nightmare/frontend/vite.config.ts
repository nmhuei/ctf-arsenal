import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    root: '.',
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      proxy: {
        '/api/flag': {
          target: env.FLAG_SERVICE_DEV_URL || 'http://localhost:3001',
          rewrite: (path) => path.replace(/^\/api\/flag\/registration-(options|verify)$/, '/registration/$1'),
        },
        '/api': 'http://localhost:3000',
      },
    },
  };
});
