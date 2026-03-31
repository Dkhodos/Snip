import path from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
	},
	test: {
		environment: "jsdom",
		setupFiles: ["./src/test/setup.ts"],
		include: ["src/**/*.test.{ts,tsx}"],
		exclude: ["src/routeTree.gen.ts", "node_modules", "dist"],
		coverage: {
			provider: "v8",
			include: ["src/**/*.{ts,tsx}"],
			exclude: [
				"src/routeTree.gen.ts",
				"src/main.tsx",
				"src/routes/**",
				"src/components/ui/**",
				"src/test/**",
			],
		},
	},
});
