import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";
import path from "path";

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    tailwindcss(),
    react({
      babel: {
        plugins: [["babel-plugin-react-compiler"]],
      },
    }),
    svgr({
      svgrOptions: {
        exportType: "default",
        ref: true,
        icon: true,
        svgo: true,
        titleProp: true,
      },
      include: ["**/*.svg"],
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@app": path.resolve(__dirname, "src/app"),
      "@pages": path.resolve(__dirname, "src/pages"),
      "@widgets": path.resolve(__dirname, "src/widgets"),
      "@features": path.resolve(__dirname, "src/features"),
      "@entities": path.resolve(__dirname, "src/entities"),
      "@shared": path.resolve(__dirname, "src/shared"),
      "@lib": path.resolve(__dirname, "src/lib"),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: true,
    server: {
      deps: {
        inline: ["@tanstack/react-query"],
      },
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        "src/test/",
        "**/*.d.ts",
        "**/*.config.*",
        "**/dist/",
      ],
    },
  },
  ssr: {
    noExternal: ["@tanstack/react-query"],
    resolve: {
      conditions: ["development", "browser"],
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Разделение vendor библиотек на отдельные чанки
          if (id.includes("node_modules")) {
            if (id.includes("react") || id.includes("react-dom") || id.includes("react-router")) {
              return "react-vendor";
            }
            if (id.includes("@tanstack/react-query")) {
              return "query-vendor";
            }
            if (id.includes("recharts")) {
              return "recharts-vendor";
            }
            if (id.includes("lucide-react") || id.includes("framer-motion")) {
              return "ui-vendor";
            }
            // Остальные node_modules в отдельный чанк
            return "vendor";
          }
        },
      },
    },
    chunkSizeWarningLimit: 600,
  },
}));
