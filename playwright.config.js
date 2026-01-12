const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://127.0.0.1:8000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "e2e",
      testMatch: /tests\/e2e\/.*\.spec\.js/,
      use: {
        browserName: "chromium",
      },
    },
    {
      name: "api",
      testMatch: /tests\/http\/.*\.spec\.js/,
    },
  ],
});
