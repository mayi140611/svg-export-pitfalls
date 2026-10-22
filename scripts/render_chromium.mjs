// Render an SVG with headless Chromium (puppeteer-core).
// usage: node render_chromium.mjs <svg> <out.png> <W> <H> <dpr> [mode] [cssW] [cssH]
// modes:
//   inline     : SVG inlined into HTML; root svg sized by its own width/height attrs
//   inlinecss  : SVG inlined into HTML; root svg width/height FORCED by CSS to cssW x cssH
//   img        : SVG loaded via <img>, CSS box cssW x cssH
//   doc        : navigate straight to the .svg file (standalone SVG document)
import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const CHROME = '/snap/chromium/current/usr/lib/chromium-browser/chrome';
const [, , svgPath, outPath, wStr, hStr, dprStr, mode = 'inline', cssW, cssH] = process.argv;
const W = parseInt(wStr), H = parseInt(hStr), dpr = parseFloat(dprStr || '1');
const svg = fs.readFileSync(svgPath, 'utf8');
const svgAbs = path.resolve(svgPath);
const dir = path.dirname(path.resolve(outPath));

const browser = await puppeteer.launch({
  executablePath: CHROME, headless: true,
  args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--disable-lcd-text',
         '--allow-file-access-from-files', '--force-color-profile=srgb'],
});
const page = await browser.newPage();
await page.setViewport({ width: W, height: H, deviceScaleFactor: dpr });

if (mode === 'doc') {
  await page.goto('file://' + svgAbs, { waitUntil: 'networkidle0' });
} else {
  const htmlPath = path.join(dir, '__wrapper.html');
  let body;
  if (mode === 'img') {
    body = `<img src="file://${svgAbs}">`;
  } else if (mode === 'inlinecss') {
    body = svg.replace(/<svg([^>]*)>/, `<svg$1 style="width:${cssW || W}px;height:${cssH || H}px">`);
  } else {
    body = svg;
  }
  const extra = mode === 'img' ? `img{display:block;width:${cssW || W}px;height:${cssH || H}px}` : '';
  fs.writeFileSync(htmlPath, `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;overflow:hidden;background:#fff}
svg{display:block}${extra}</style></head><body>${body}</body></html>`);
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle0' });
}
await new Promise(r => setTimeout(r, 150));
await page.screenshot({ path: outPath, clip: { x: 0, y: 0, width: W, height: H } });
await browser.close();
const { execSync } = await import('child_process');
console.log(execSync(`file ${outPath}`).toString().trim());
