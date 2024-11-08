// babel.config.mjs
export default {
  presets: [
    [
      "@babel/preset-env",
      {
        targets: { node: "current" },
        modules: "auto", // This helps with ESM/CommonJS interop
      },
    ],
    ["@babel/preset-react", { runtime: "automatic" }],
  ],
  assumptions: {
    privateFieldsAsProperties: true,
    setPublicClassFields: true,
  },
};
