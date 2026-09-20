import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";

const root = resolve(fileURLToPath(new URL("../", import.meta.url)));
const read = (file) => readFileSync(resolve(root, file), "utf8");

const html = read("web/index.html");
const js = read("web/app.js");
const css = read("web/styles.css");

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
if (html.includes("<style>")) {
  throw new Error("Inline CSS should not be used in rebuilt frontend.");
}
if (html.includes("<script>")) {
  throw new Error("Inline JavaScript should not be used in rebuilt frontend.");
}

console.log("FRONTEND SMOKE PASSED");
