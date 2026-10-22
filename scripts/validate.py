import re, os
f='2026-10-22-svg-export-troubleshooting.md'
s=open(f,encoding='utf-8').read()
m=re.match(r'^---\n(.*?)\n---\n', s, re.S); fm=m.group(1); body=s[m.end():]
def cjk(t): return len(re.findall(r'[\u4e00-\u9fff]', t))
nocode=re.sub(r'```.*?```','',body,flags=re.S)
ex=re.search(r'^excerpt:\s*"(.*)"$', fm, re.M).group(1)
print('=== 字数 ===')
n=cjk(nocode)
print('  正文 CJK（不含代码块）= %d  要求 2400-3200 -> %s' % (n, 'OK' if 2400<=n<=3200 else '超范围'))
print('  正文 CJK（含代码块）  = %d' % cjk(body))
print('  excerpt CJK           = %d  要求 40-60 -> %s' % (cjk(ex), 'OK' if 40<=cjk(ex)<=60 else '超范围'))
print('\n=== frontmatter 4 字段 ===')
for k in ['title','date','tags','excerpt']:
    mm=re.search(r'^%s:\s*(.*)$'%k, fm, re.M)
    print('  %s %s' % ('OK ' if mm else '缺失', k))
print('\n=== 图片 ===')
base='/home/emp001/Documents/agent_workspace/p2p/ou_cae300ff8d233e62ec5c3532f13d0333/projects/20261012124000_时空猫博客站/docs/public'
seen=set()
for alt,p in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', body):
    fp=os.path.join(base,p.lstrip('/'))
    print('  %s %-42s alt(%d字) %s' % ('OK ' if os.path.exists(fp) else '缺失', p, len(alt), alt))
    seen.add(p)
print('  图片数(去重)=%d' % len(seen))
print('\n=== 相对链接 ===')
for text,p in re.findall(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)', body):
    if p.startswith('http'): continue
    full=os.path.join(os.path.dirname(f), p.split('#')[0]+'.md')
    print('  %s %-48s -> %s  结尾斜杠=%s' % ('OK ' if os.path.exists(full) else '缺失', p, os.path.basename(full), p.endswith('/')))
print('\n=== 外链 ===')
for p in sorted(set(re.findall(r'\((https?://[^)]+)\)', body))):
    print('  %-50s 出现 %d 次' % (p, body.count(p)))
print('\n=== 禁用项自检 ===')
for kw in ['欢迎留言','收益','荐股','稳赚','保证收益','留言区']:
    print('  %s %s' % ('命中!' if kw in body else '无  ', kw))
