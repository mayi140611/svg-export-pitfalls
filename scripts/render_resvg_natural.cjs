const { Resvg } = require('@resvg/resvg-js');
const fs = require('fs'); const { execSync } = require('child_process');
const [, , svgPath, outPath, dpiStr, fontOpt] = process.argv;
const svg = fs.readFileSync(svgPath, 'utf8');
const fontOpts = { loadSystemFonts: true };
if (fontOpt && fs.existsSync(fontOpt)) { fontOpts.fontFiles = [fontOpt]; fontOpts.loadSystemFonts = false; }
const opts = { fitTo: { mode: 'original' }, font: fontOpts };
if (dpiStr) opts.dpi = parseFloat(dpiStr);
const png = new Resvg(svg, opts).render();
fs.writeFileSync(outPath, png.asPng());
console.log(execSync(`file ${outPath}`).toString().trim() + `  [resvg natural dpi=${opts.dpi||96}]`);
