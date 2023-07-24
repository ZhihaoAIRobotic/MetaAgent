const config = {
  plugins: [
    require("prettier-plugin-tailwindcss"),
    "@trivago/prettier-plugin-sort-imports",
  ],
  tailwindConfig: "./tailwind.config.js",
  pluginSearchDirs: false,
  trailingComma: "all",
  printWidth: 80,
  tabWidth: 2,
  arrowParens: "always",
  semi: true,
  singleQuote: false,
  useTabs: false,
  importOrder: [
    "<THIRD_PARTY_MODULES>",
    "^@/*/(.*)$",
    "^[../]",
    "^[./]",
    "^import type(.*)from(.*)$",
  ],
  importOrderSeparation: true,
};

module.exports = config;
