# svg-export-pitfalls — SVG 导出「糊了」的最小复现集

> 27 个最小复现 SVG + 三套栅格化器的对照结果，用来回答一个问题：
> **SVG 号称无损，为什么导出成 PNG 就糊了？**

配套长文（完整推导、8 个坑逐条展开、像素级数据）：
**<https://cosmocat.dev/ai/posts/2026-10-22-svg-export-troubleshooting>**

相关工具页（矢量编辑工作台，中文实测）：<https://craft.cosmocat.dev/app/vectorcraft>

---

## 一句话结论

**SVG 文件本身几乎不会「糊」。糊的一定是栅格化那一步**——要么你导出的分辨率不对，
要么那个渲染器压根不支持你文件里的某个特性，**而且不报错**。

本仓库把这句话拆成 8 个可独立复现的坑，每个都量到了具体像素和字节。

## 8 个坑与实测数字

| # | 坑 | 复现文件 | 实测结果 |
|---|---|---|---|
| 1 | 缺 `viewBox` | `exp/e1_with_vb.svg` / `e1_no_vb.svg` | 有 viewBox 红块 bbox `(40,40)–(119,119)`；无 viewBox `(20,20)–(59,59)`，**完全不缩放**。同一文件改用 `<img>` 引入，三套渲染器又都回到 `(40,40)–(119,119)` —— **同一浏览器同一文件，换挂法结果就反了** |
| 2 | `pt` / `px` 混用 | `exp/e2_pt.svg` / `e2_px.svg` / `e2b_illustrator.svg` | `width="600pt"` 在 Chromium / resvg(dpi96) / cairosvg(dpi96) 下全出 **800×533**；dpi=72 才出 600×400。比值 **1.3333** |
| 3 | 只导 1x | `exp/e3_detail.svg` | 1x=400×300 / **8,792 B**；2x=800×600 / **18,698 B**（2.13×）；3x=1,200×900 / **31,230 B**（3.55×）。把 1x 拉伸到 800×600 后 Laplacian 方差 **276.0**，2x 原生 **1210.1** → **锐 4.38×** |
| 4 | 字体没内嵌 | `exp/e4_a.svg` / `e4_a_paths.svg` / `e4_b~d.svg` | 墨迹宽：Noto Sans CJK SC **359px**；字体不存在→回退 **341px**（**−5.0%**）；Mono CJK **376px**（+4.7%）；仅 DejaVu **323px** 且中文成 4 个豆腐块 □□□□。转曲后体积 **259 B → 7,727 B**（**29.83×**） |
| 5 | `transform` / 坐标 | `exp/e5_rotate.svg` / `e5_clip.svg` | 200×200 画布里 (150,150) 起的 100×100 方块**只剩 50×50，丢一半**；`rotate(45)` 绕原点使 100×20 横条 bbox 变成 x `0..69` / y `1..83`；内嵌位图 12×12→48×48 后 Laplacian **56.6** vs 原生 **2980.4**（**52.7×**） |
| 6 | 渐变 / 滤镜 / 混合模式 | `exp/e6_blur.svg` / `e6_grad_*.svg` / `e6b_*.svg` | 渐变：三工具最大通道偏差 **≤1**，无实质差异。`feGaussianBlur` x=30 剖面 Chrome `139→116→93`、resvg `139→116→95`、**cairosvg 从 255 硬跳到 0**。`feDropShadow` 暗像素 Chrome **1,486** / resvg **1,476** / cairosvg **1,272**。multiply：写成**表现属性** `mix-blend-mode="multiply"` 出 `(128,128,128)` 等于没混合，写成 CSS `style` 才出 `(128,0,0)` |
| 7 | 颜色写法 | `exp/colors/` | cairosvg：`hsl()`/`hsla()` → 纯黑 `(0,0,0)`；8 位 hex `#ff000080` → `(255,0,0)` **alpha 被丢**；`rgb(0 0 0 / 50%)` → **ValueError 崩溃**。resvg：`rgb(255 0 0 / 50%)` → 变黑；`oklch()` → 变黑 |
| 8 | 半像素描边 | `exp/e8_halfpixel.svg` | 灰度剖面：1x `y=30` 跨 2 行 **128/127**（糊）；`y=60.5` 单行 **0**（锐）。**2x 下两者都落整数设备行，都清晰** —— 半像素对齐只针对 1x |

性能（2000 path / 1000×1000）：Chromium 热渲染中位 **68ms**、resvg **107.9ms**、cairosvg **150.7ms**。

## 复现方式

三套独立的栅格化器，交叉验证用：

```bash
# 1) Chromium（无头）
node scripts/render_chromium.mjs exp/e1_with_vb.svg out.png 400 200 1 inlinecss 400 200

# 2) resvg（Rust，贴近浏览器）
node scripts/render_resvg.cjs exp/e4_a.svg out.png 600 72

# 3) cairosvg（Python）
python3 scripts/render_cairo.py exp/e2b_illustrator.svg out.png 96
```

`scripts/validate.py` 做像素级对比（bbox / Laplacian 锐度 / 灰度剖面），
`scripts/text_to_path.py` 是把文字转曲的复现脚本。

## 目录

```
exp/          27 个最小复现 SVG（每个坑 2-3 个变体）
results/      三套渲染器的对照输出（PNG）
scripts/      渲染与像素分析脚本
```

## 测试环境

- Linux aarch64，无头 Chromium（`--headless`，SwiftShader 软渲染）
- resvg（`@resvg/resvg-js`）、cairosvg 2.9.1
- 系统装了 109 个中文字体，含 Noto Sans CJK SC、Noto Sans Mono CJK SC、AR PL UMing CN

**未在本仓库验证的**：Inkscape、librsvg（`rsvg-convert`）、ImageMagick 的实际行为——测试机上未安装，
跨工具对比只覆盖上面三套。字体相关的「目标机器」是用 resvg 限制字体集模拟的，不是真的换了一台机器。

## License

MIT —— 见 [LICENSE](LICENSE)。

代码与数据均为本人实测产出。文中提到的软件均为第三方开源项目，本仓库与其无关联。
