import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";

const root = resolve(fileURLToPath(new URL("../", import.meta.url)));
const read = (file) => readFileSync(resolve(root, file), "utf8");

const html = read("frontend/index.html");
const js = read("frontend/app.js");
const css = read("frontend/styles.css");

const requiredHtml = [
  'href="/styles.css"',
  'defer src="/app.js"',
  'id="loggedOut"',
  'id="loggedIn"',
  'id="settingsLanguage"',
  'id="settingsTheme"',
  'id="scraperUrl"',
  'id="lightsGrid"',
];

for (const marker of requiredHtml) {
  if (!html.includes(marker)) {
    throw new Error(`Missing frontend marker: ${marker}`);
  }
}

const requiredJs = [
  "/api/auth/status",
  "/api/gateway/health",
  "/api/auth/register",
  "/api/auth/login",
  "/api/auth/google/start",
  "/api/auth/settings",
  "/api/auth/profile",
  "/api/auth/password",
  "/api/scraper/fetch",
  "/api/scraper/crawl",
  "/api/assets/roblox/validate",
  "/api/sprite-sheet/extract",
];

for (const marker of requiredJs) {
  if (!js.includes(marker)) {
    throw new Error(`Missing frontend gateway route: ${marker}`);
  }
}

if (!css.includes("@media (max-width:640px)")) {
  throw new Error("Responsive mobile breakpoint is missing.");
}
if (!css.includes("@media (prefers-reduced-motion:reduce)")) {
  throw new Error("Reduced-motion support is missing.");
}
if (/<style\b/i.test(html) || /<script\s*>/i.test(html)) {
  throw new Error("Inline CSS/JavaScript should not be used in rebuilt frontend.");
}
if (html.includes("onclick=") || /\sstyle="/i.test(html)) {
  throw new Error("Inline event handlers/style attributes should not be used in rebuilt frontend.");
}
if (!html.includes('PT. NARARYA JAYA UTAMA GROUB - All Right Reserved')) {
  throw new Error("Corporate footer is missing.");
}
if (!js.includes("const ACTIONS=") || !js.includes("repository_folders") || !js.includes('document.addEventListener("click"')) {
  throw new Error("JavaScript action delegation is missing.");
}

console.log("FRONTEND SMOKE PASSED");
