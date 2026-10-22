# -*- coding: utf-8 -*-
"""生成博客配图。所有素材来自 /tmp/svgtest/exp 下的真实渲染结果。"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = '/home/emp001/Documents/agent_workspace/p2p/ou_cae300ff8d233e62ec5c3532f13d0333/projects/20261012124000_时空猫博客站/docs/public/images/svg'
os.makedirs(OUT, exist_ok=True)
E = '/tmp/svgtest/exp'

TTC = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(sz, bold=False):
    path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if bold else TTC
    for idx in range(0, 12):
        try:
            f = ImageFont.truetype(path, sz, index=idx)
            if f.getname()[0].startswith('Noto Sans CJK SC'):
                return f
        except Exception:
            continue
    return ImageFont.truetype(TTC, sz, index=0)

F14, F16, F18, F22 = font(14), font(16), font(18), font(22)
F14b, F16b, F18b = font(14, True), font(16, True), font(18, True)
MONO = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 13)

BG, FG, MUTED, RED, GREEN, BLUE = '#ffffff', '#1a1a1a', '#666666', '#d93025', '#137333', '#1a73e8'
PAD = 28


def label(d, x, y, txt, f=F16, fill=FG):
    d.text((x, y), txt, font=f, fill=fill)


def wrap(d, text, f, width):
    lines, cur = [], ''
    for ch in text:
        if d.textlength(cur + ch, font=f) > width:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur: lines.append(cur)
    return lines


# ---------------------------------------------------------------- 图1 字体
def img_font():
    rows = [
        (f'{E}/e4_a_chrome.png', '① font-family="Noto Sans CJK SC"', '本机装了 → 正常', GREEN, 359),
        (f'{E}/e4_b_chrome.png', '② font-family="SuperFancyDisplay"', '本机没装 → 回退到别的字体，字宽 359→341px', '#b06000', 341),
        (f'{E}/e4_a_rsvg_dejavu.png', '③ 目标机器只有 DejaVu Sans', '没有中文字体 → 中文直接变豆腐块', RED, 323),
    ]
    W = 780
    crop = (0, 28, 460, 82)
    panel_h = 76
    H = PAD + 44 + len(rows) * (panel_h + 16) + PAD
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    label(d, PAD, PAD, '同一个 SVG，三台机器，三种结果', F18b)
    d.text((PAD, PAD + 24), 'font-size:40px   内容：「矢量图形 Vector 123」', font=F14, fill=MUTED)
    y = PAD + 48
    for path, title, note, color, w in rows:
        d.rectangle([PAD, y, W - PAD, y + panel_h], outline='#e0e0e0')
        d.rectangle([PAD, y, PAD + 5, y + panel_h], fill=color)
        src = Image.open(path).convert('RGB').crop(crop)
        im.paste(src, (PAD + 18, y + 10))
        d.text((PAD + 18, y + panel_h - 20), title, font=F14, fill=MUTED)
        d.text((PAD + 490, y + 8), note.split('→')[0].strip(), font=F14b, fill=color)
        d.text((PAD + 490, y + 26), '→'.join(note.split('→')[1:]).strip(), font=F14, fill=MUTED)
        d.text((PAD + 490, y + 46), f'墨迹宽 {w}px', font=F14b, fill=FG)
        y += panel_h + 16
    d.text((PAD, H - PAD - 4), 'Chromium 渲染截图；③ 用 resvg 只喂 DejaVuSans.ttf 模拟', font=F14, fill=MUTED)
    im.save(f'{OUT}/font-fallback.png')
    print('font-fallback.png', im.size)


# ------------------------------------------------------------ 图2 viewBox
def img_viewbox():
    a = Image.open(f'{E}/e1_vb_css.png').convert('RGB')   # 有 viewBox
    b = Image.open(f'{E}/e1_novb_css.png').convert('RGB') # 无 viewBox
    cell = 400
    W = PAD * 2 + cell * 2 + 24
    H = PAD + 46 + cell + 96
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    label(d, PAD, PAD, '同一个 200×100 的 SVG，CSS 强制拉到 400×200', F18b)
    im.paste(a, (PAD, PAD + 40))
    im.paste(b, (PAD + cell + 24, PAD + 40))
    d.rectangle([PAD, PAD + 40, PAD + cell, PAD + 40 + cell], outline='#e0e0e0')
    d.rectangle([PAD + cell + 24, PAD + 40, PAD + cell * 2 + 24, PAD + 40 + cell], outline='#e0e0e0')
    d.text((PAD, PAD + 46 + cell), '✓ 有 viewBox="0 0 200 100"', font=F16b, fill=GREEN)
    d.text((PAD + cell + 24, PAD + 46 + cell), '✗ 没有 viewBox', font=F16b, fill=RED)
    # 期望位置 2x 虚线框
    for x0 in (PAD, PAD + cell + 24):
        for i in range(0, 80, 12):
            d.rectangle([x0 + 40 + i, PAD + 40 + 40, x0 + 40 + i + 6, PAD + 40 + 41], fill='#999999')
            d.rectangle([x0 + 40 + i, PAD + 40 + 80, x0 + 40 + i + 6, PAD + 40 + 81], fill='#999999')
        d.rectangle([x0 + 40, PAD + 40 + 40, x0 + 120, PAD + 40 + 80], outline='#999999')
    d.text((PAD, PAD + 46 + cell + 24), '虚线 = 「应该」被放大到 2 倍的位置（40,40 → 120,120）', font=F14, fill=MUTED)
    d.text((PAD + cell + 24, PAD + 46 + cell + 24), '实际仍停在 (20,20) → (60,60)：内容没跟着缩放', font=F14, fill=MUTED)
    im.save(f'{OUT}/viewbox-missing.png')
    print('viewbox-missing.png', im.size)


# --------------------------------------------------------------- 图3 DPR
def img_dpr():
    a = Image.open(f'{E}/e3_1x.png').convert('RGB')
    b = Image.open(f'{E}/e3_2x.png').convert('RGB')
    box = (35, 200, 235, 240)          # 1x 坐标：文字带
    box2 = (70, 400, 470, 480)         # 2x 坐标
    ca = a.crop(box).resize((600, 120), Image.LANCZOS)          # 1x PNG 被浏览器拉成 2x
    cb = b.crop(box2).resize((300, 60), Image.LANCZOS).resize((600, 120), Image.LANCZOS)  # 2x PNG 缩回 CSS 尺寸
    W = PAD * 2 + 600
    H = PAD + 52 + 120 + 32 + 120 + 34 + PAD
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    label(d, PAD, PAD, '400×300 的 SVG，在 2 倍屏上显示', F18b)
    d.text((PAD, PAD + 26), '左：导出 1x PNG，被浏览器拉伸到 2 倍    右：导出 2x PNG，缩回 CSS 尺寸', font=F14, fill=MUTED)
    y = PAD + 52
    im.paste(ca, (PAD, y))
    d.rectangle([PAD, y, PAD + 600, y + 120], outline='#e0e0e0')
    d.text((PAD, y + 126), '1x PNG：Laplacian 方差 276（模糊）', font=F16b, fill=RED)
    y += 120 + 34
    im.paste(cb, (PAD, y))
    d.rectangle([PAD, y, PAD + 600, y + 120], outline='#e0e0e0')
    d.text((PAD, y + 126), '2x PNG：Laplacian 方差 1210（锐 4.38 倍）', font=F16b, fill=GREEN)
    im.save(f'{OUT}/dpr-1x-vs-2x.png')
    print('dpr-1x-vs-2x.png', im.size)


# -------------------------------------------------- 图4 半像素描边
def img_halfpixel():
    src = Image.open(f'{E}/e8_1x.png').convert('L')
    top = src.crop((60, 26, 140, 34))     # y=30 整线
    bot = src.crop((60, 56, 140, 64))     # y=60.5 半线
    Z = 8
    top = top.resize((top.width * Z, top.height * Z), Image.NEAREST).convert('RGB')
    bot = bot.resize((bot.width * Z, bot.height * Z), Image.NEAREST).convert('RGB')
    LW = 300
    W = PAD * 2 + top.width + 20 + LW
    H = PAD + 52 + top.height + 42 + bot.height + PAD + 26
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    label(d, PAD, PAD, '1px 黑色描边在 1x 栅格化下的两种结果（放大 8 倍）', F18b)
    d.text((PAD, PAD + 26), 'stroke-width:1   背景纯白', font=F14, fill=MUTED)
    y = PAD + 52
    im.paste(top, (PAD, y))
    d.rectangle([PAD, y, PAD + top.width, y + top.height], outline='#e0e0e0')
    tx = PAD + top.width + 20
    d.text((tx, y + 4), 'y=30（整数坐标）', font=F16b, fill=RED)
    d.text((tx, y + 30), '跨了 2 行，灰度 128 / 127', font=F14, fill=MUTED)
    d.text((tx, y + 50), '→ 糊成 2px', font=F14b, fill=RED)
    y += top.height + 42
    im.paste(bot, (PAD, y))
    d.rectangle([PAD, y, PAD + bot.width, y + bot.height], outline='#e0e0e0')
    d.text((tx, y + 4), 'y=60.5（半像素坐标）', font=F16b, fill=GREEN)
    d.text((tx, y + 30), '只占 1 行，纯 0 黑', font=F14, fill=MUTED)
    d.text((tx, y + 50), '→ 锐利 1px', font=F14b, fill=GREEN)
    d.text((PAD, H - PAD - 8), 'Chromium 1x 渲染（400×120）截取的真实像素', font=F14, fill=MUTED)
    im.save(f'{OUT}/half-pixel-stroke.png')
    print('half-pixel-stroke.png', im.size)


for f in (img_font, img_viewbox, img_dpr, img_halfpixel):
    f()
