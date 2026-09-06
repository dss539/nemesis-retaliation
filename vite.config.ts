import { defineConfig } from 'vite';

export default defineConfig({
  base: '/nemesis-retaliation/',
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  preview: {
    allowedHosts: ['smithers.coyote-piranha.ts.net', '.ts.net', 'localhost', '127.0.0.1'],
  },
  server: {
    allowedHosts: ['smithers.coyote-piranha.ts.net', '.ts.net', 'localhost', '127.0.0.1'],
  },
});
