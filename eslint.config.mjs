import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";
import { globalIgnores } from "eslint/config";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // Frontend now lives at the repo root alongside backend/, which is a
    // separate Python project (including a vendored .venv full of JS files
    // from site-packages) — without this, ESLint has no folder scoping and
    // tries to lint the entire monorepo.
    "backend/**",
  ]),
];

export default eslintConfig;
