import { defineConfig } from "vite";
import { resolve } from "node:path";

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        home: resolve(import.meta.dirname, "index.html"),
        professionals: resolve(import.meta.dirname, "professionals.html"),
        insights: resolve(import.meta.dirname, "insights.html"),
        systems: resolve(import.meta.dirname, "systems.html")
      }
    }
  }
});
