"""把 SVG 里的 <text> 转成 <path>（模拟设计软件「转曲」导出），并对比体积/渲染一致性。"""
import sys, os, glob
from fontTools.ttLib import TTCollection, TTFont
from fontTools.pens.svgPathPen import SVGPathPen

FONT_CANDIDATES = sorted(glob.glob('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'))

def load_cjk_sc():
    for path in FONT_CANDIDATES:
        coll = TTCollection(path, lazy=True)
        for i, f in enumerate(coll.fonts):
            names = {n.toUnicode() for n in f['name'].names if n.nameID == 1}
            if 'Noto Sans CJK SC' in names:
                return path, i, f
    raise SystemExit('font not found')

def main(src, dst, text, x, y, size):
    path, idx, font = load_cjk_sc()
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    upem = font['head'].unitsPerEm
    scale = size / upem
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="120" viewBox="0 0 600 120">',
           f'<rect width="600" height="120" fill="#ffffff"/>']
    pen_x = x
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            continue
        spen = SVGPathPen(gs, ntos=lambda v: f'{v:.3f}')
        gs[gname].draw(spen)
        d = spen.getCommands()
        if d:
            out.append(f'<g transform="translate({pen_x:.3f},{y:.3f}) scale({scale:.6f},{-scale:.6f})">'
                       f'<path d="{d}" fill="#000000"/></g>')
        pen_x += gs[gname].width * scale
    out.append('</svg>')
    open(dst, 'w').write('\n'.join(out))
    print(f'wrote {dst}  bytes={os.path.getsize(dst)}')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]))
