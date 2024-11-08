// jest.config.mjs
export default {
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.mjs"],
  moduleNameMapper: {
    "\\.(css|less|sass|scss)$": "identity-obj-proxy",
    "\\.(jpg|jpeg|png|gif|webp|svg)$": "<rootDir>/__mocks__/fileMock.js",
  },
  transform: {
    "^.+\\.(js|jsx)$": "babel-jest",
  },
  extensionsToTreatAsEsm: [".jsx"],
  moduleFileExtensions: ["js", "jsx", "mjs"],
  testMatch: ["**/__tests__/**/*.test.jsx"],
};
