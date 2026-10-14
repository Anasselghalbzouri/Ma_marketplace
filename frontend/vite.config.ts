/// <reference types="vitest" />
/// <reference types="vite/client" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

// T-012 — socle frontend mobile-first. Vite + React 19 + TS strict.
// Le proxy `/api` et `/photos` permet de brancher le backend Laravel dès qu'il
// est démarrable (étape 4.x — Anvil). Voir docs/integration.md.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: false,
        // Si le backend n'est pas démarré, Vite renverra 502 ; le frontend le
        // traduit en `server_error` (cf. src/api/errorEnvelope.ts).
      },
      '/photos': {
        target: 'http://localhost:8080',
        changeOrigin: false,
      },
    },
  },
  preview: {
    host: '127.0.0.1',
    port: 4173,
    strictPort: true,
  },
  // @ts-expect-error -- vitest ajoute `test` à UserConfig ; on garde defineConfig
  // de vite pour l'IDE sans dépendre de vitest/config à l'exécution.
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    css: false,
  },
});