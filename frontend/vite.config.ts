import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],

  // Production optimizations
  build: {
    // Generate sourcemaps for production debugging (optional, remove if not needed)
    sourcemap: false,

    // Reduce chunk size warnings threshold
    chunkSizeWarningLimit: 1000,

    // Optimize bundle splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor code into separate chunk
          vendor: ['react', 'react-dom'],
          icons: ['lucide-react'],
        },
      },
    },

    // Minification - use esbuild (default, faster)
    minify: 'esbuild',
  },

  // Preview server configuration
  preview: {
    port: 5173,
    strictPort: false,
    open: true,
  },

  // Development server configuration
  server: {
    port: 5173,
    strictPort: false,
    open: false,
  },
})
