// node tools/run_page.mjs <url> [timeoutSec] — open a page in headless Chromium and wait for title DONE/FAIL.
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const [url, t = '300'] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage();
p.on('console', m => console.log('[page]', m.text())); p.on('pageerror', e => console.log('[err]', e.message));
await p.goto(url);
await p.waitForFunction(() => document.title.startsWith('DONE') || document.title.startsWith('FAIL'), null, { timeout: +t * 1000 });
console.log(await p.title()); await b.close();
