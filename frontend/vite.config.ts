import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// Tailwind CSS is handled via PostCSS; no Vite plugin needed

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
});
