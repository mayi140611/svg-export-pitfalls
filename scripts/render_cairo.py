import sys, time, subprocess
import cairosvg

svg_path, out_path = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else None
t0 = time.perf_counter()
cairosvg.svg2png(url=svg_path, write_to=out_path,
                 output_width=width, dpi=float(sys.argv[5]) if len(sys.argv)>5 else 96,
                 background_color=None if len(sys.argv) <= 4 else sys.argv[4])
ms = (time.perf_counter() - t0) * 1000
print(subprocess.run(['file', out_path], capture_output=True, text=True).stdout.strip() + f"  [cairosvg {ms:.1f}ms]")
