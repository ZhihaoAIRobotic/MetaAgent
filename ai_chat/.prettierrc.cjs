/** @type {import('prettier').Config} */
module.exports = {
  trailingComma: "all",
  printWidth: 80,
  tabWidth: 2,
  arrowParens: "always",
  semi: true,
  singleQuote: false,
  useTabs: false,
  plugins: [
    "@trivago/prettier-plugin-sort-imports",
    "prettier-plugin-tailwindcss",
  ],
  importOrder: [
    "<THIRD_PARTY_MODULES>",
    "^@/*/(.*)$",
    "^[../]",
    "^[./]",
    "^import type(.*)from(.*)$",
  ],
  importOrderSeparation: true,
  importOrderSortSpecifiers: true,
};
