import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Enable SPA mode for client-side routing
    open: true,
    proxy: {
      // Proxy API requests to backend
      '/api': {
        target: 'http://durable-code-backend-dev:8000',
        changeOrigin: true,
        ws: true, // Enable WebSocket proxy
      },
    },
  },
  preview: {
    port: 5173,
  },
});
