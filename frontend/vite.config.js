import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      // Any request starting with /api will be sent to your backend
      '/api': {
        target: 'http://localhost:3000', // CHANGE THIS to your actual backend port
        changeOrigin: true,
        secure: false,
      }
    }
  }
})