import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Enable SPA mode for client-side routing
    open: true,
  },
  preview: {
    port: 5173,
  },
});
