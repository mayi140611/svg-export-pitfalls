const { Resvg } = require('@resvg/resvg-js');
const fs = require('fs'); const path = require('path'); const { execSync } = require('child_process');
const [, , svgPath, outPath, wStr, dpiStr, fontOpt] = process.argv;
const W = parseInt(wStr);
const svg = fs.readFileSync(svgPath, 'utf8');
const fontOpts = { loadSystemFonts: true };
if (fontOpt && fs.existsSync(fontOpt)) { fontOpts.fontFiles = [fontOpt]; fontOpts.loadSystemFonts = false; }
const opts = { fitTo: { mode: 'width', value: W }, font: fontOpts };
if (dpiStr) opts.dpi = parseFloat(dpiStr);
const t0 = process.hrtime.bigint();
const resvg = new Resvg(svg, opts);
const png = resvg.render();
const ms = Number(process.hrtime.bigint() - t0) / 1e6;
fs.writeFileSync(outPath, png.asPng());
console.log(execSync(`file ${outPath}`).toString().trim() + `  [resvg dpi=${opts.dpi||96} ${ms.toFixed(1)}ms]`);
