import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      // Force React to resolve to a single instance
      "react": path.resolve(__dirname, "./node_modules/react"),
      "react-dom": path.resolve(__dirname, "./node_modules/react-dom"),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Keep the /api prefix as backend expects it
        rewrite: (path) => path
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Keep '/auth' so backend receives '/auth/*'
        rewrite: (path) => path
      },
      '/hr': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      // Only proxy manager API calls, not the page itself
      '/manager/applications': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/manager/property': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/manager/dashboard-stats': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/properties': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/applications': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/onboarding': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Rewrite /onboarding to /api/onboarding to match backend routes
        rewrite: (path) => path.replace(/^\/onboarding/, '/api/onboarding')
      },
      '/notifications': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    },
    // Optimize HMR for better memory usage
    hmr: {
      overlay: false
    }
  },
  optimizeDeps: {
    // Force include React to ensure single instance
    include: ['react', 'react-dom', 'react-router-dom', 'axios', 'react-hook-form'],
    // Force esbuild to use our aliased versions
    esbuildOptions: {
      preserveSymlinks: false
    }
  },
  build: {
    // Reduce memory usage during build
    sourcemap: false,
    // Increase chunk size warning limit
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        // Enhanced code splitting for better performance
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          radixUI: [
            '@radix-ui/react-dialog',
            '@radix-ui/react-select',
            '@radix-ui/react-checkbox',
            '@radix-ui/react-radio-group',
            '@radix-ui/react-tabs',
            '@radix-ui/react-toast'
          ],
          forms: ['react-hook-form', '@hookform/resolvers', 'zod'],
          utils: ['axios', 'date-fns', 'clsx', 'tailwind-merge']
        }
      }
    }
  },
  // Prevent memory leaks in development
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' }
  }
})