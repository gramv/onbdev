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
    // Dedupe React to prevent duplicate instances
    dedupe: ['react', 'react-dom'],
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      // Single proxy rule for all API endpoints
      // All API calls should use /api prefix
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Keep the /api prefix as backend will expect it
        rewrite: (path) => path,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.error('Proxy error:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Proxying:', req.method, req.url, '->', options.target + req.url);
          });
        }
      },
      // WebSocket proxy for real-time updates
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
      },
      // Legacy endpoints - will be removed after backend migration
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/properties': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/notifications': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/onboarding': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/secret': {
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