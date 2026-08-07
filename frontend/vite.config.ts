import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

/**
 * Splits the large third-party dependencies into a few stable vendor chunks so
 * that (a) the initial payload shrinks and (b) long-lived libraries are cached
 * separately from app code (their hashes rarely change between deploys — good
 * for repeat visits over slow corporate links).
 *
 * We intentionally keep this coarse: a handful of logical vendor chunks rather
 * than dozens of micro-chunks, to avoid a request storm on high-latency VPNs.
 */
function manualChunks(id: string): string | undefined {
  if (!id.includes('node_modules')) return undefined;

  // React runtime + router — needed on every route.
  if (
    id.includes('node_modules/react/') ||
    id.includes('node_modules/react-dom/') ||
    id.includes('node_modules/react-router') ||
    id.includes('node_modules/scheduler/')
  ) {
    return 'vendor-react';
  }

  // Data layer.
  if (id.includes('node_modules/@tanstack/')) return 'vendor-query';

  // Animation library — heavy, only needed by the marketing / animated pages.
  if (
    id.includes('node_modules/framer-motion') ||
    id.includes('node_modules/motion-dom') ||
    id.includes('node_modules/motion-utils')
  ) {
    return 'vendor-motion';
  }

  // Fonts are emitted as CSS/asset files, not JS — leave them alone.
  if (id.includes('node_modules/@fontsource/')) return undefined;

  // Everything else (axios, zustand, clsx, lucide icons, toast, ...).
  return 'vendor';
}

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // Локальная разработка без nginx: проксируем API на backend (uvicorn).
    // В production /api обслуживает nginx; на сборку это не влияет.
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    target: 'es2020',
    cssCodeSplit: true,
    chunkSizeWarningLimit: 700,
    rollupOptions: {
      output: {
        manualChunks,
      },
    },
  },
});
