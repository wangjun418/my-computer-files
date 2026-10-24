import os, json, time, re
from pathlib import Path
from collections import Counter, defaultdict

NOW = time.time()
TARGETS = [Path(r'C:\Users\Lenovo\Documents'), Path(r'C:\Users\Lenovo\Desktop'), Path(r'C:\Users\Lenovo\Downloads')]
EXCLUDE_ROOTS = {
    'Windows','Program Files','Program Files (x86)','ProgramData','System Volume Information','$Recycle.Bin','Recovery','PerfLogs'
}

def human(n):
    n=float(n or 0)
    units=['B','KB','MB','GB','TB']
    i=0
    while n>=1024 and i<len(units)-1:
        n/=1024; i+=1
    return f'{n:.2f} {units[i]}'

def safe_stat(p):
    try: return p.stat()
    except Exception: return None

def scan_tree(root):
    files=[]; errors=[]; dir_stats=defaultdict(lambda: {'files':0,'bytes':0})
    if not root.exists():
        return {'path':str(root),'exists':False,'files':0,'bytes':0,'file_records':[],'errors':[f'not found: {root}'],'top_dirs':[]}
    for base, dirs, names in os.walk(root, topdown=True, onerror=lambda e: errors.append(str(e))):
        # prune junction/symlink dirs and known volatile/system subtrees under user folders
        keep=[]
        for d in dirs:
            dp=Path(base)/d
            try:
                if dp.is_symlink():
                    continue
            except Exception:
                continue
            keep.append(d)
        dirs[:] = keep
        rel=Path(base).relative_to(root)
        top = rel.parts[0] if rel.parts else '(root)'
        for name in names:
            p=Path(base)/name
            try:
                st=p.stat()
            except Exception as e:
                errors.append(f'{p}: {e}')
                continue
            ext=p.suffix.lower() or '[no extension]'
            rec={'path':str(p),'name':name,'size':st.st_size,'mtime':st.st_mtime,'ext':ext,'age_days':round((NOW-st.st_mtime)/86400,1)}
            files.append(rec)
            dir_stats[top]['files'] += 1; dir_stats[top]['bytes'] += st.st_size
    ext_counts=Counter(r['ext'] for r in files)
    ext_bytes=defaultdict(int)
    for r in files: ext_bytes[r['ext']] += r['size']
    top_files=sorted(files,key=lambda x:x['size'],reverse=True)[:50]
    # temp/cache candidates (review only)
    pat_ext={'.tmp','.temp','.log','.bak','.old','.dmp','.crdownload','.part','.cache','.pyc','.pyo','.obj','.ilk','.chk','.gid'}
    pat_parts={'cache','caches','temp','tmp','__pycache__','.ipynb_checkpoints','thumbnails'}
    candidates=[]
    for r in files:
        low=r['path'].lower()
        parts=set(x.lower() for x in Path(r['path']).parts)
        reason=[]
        if r['ext'] in pat_ext: reason.append('temporary/log/backup-like extension')
        if parts & pat_parts: reason.append('cache/temp-like directory')
        if r['name'].lower().startswith('~$'): reason.append('Office lock file')
        if reason: candidates.append({'path':r['path'],'size':r['size'],'age_days':r['age_days'],'reason':'; '.join(reason)})
    groups=defaultdict(list)
    for r in files:
        groups[(r['name'].lower(),r['size'])].append(r['path'])
    dup=[{'name':k[0],'size':k[1],'paths':v[:20],'count':len(v)} for k,v in groups.items() if len(v)>1]
    dup=sorted(dup,key=lambda x:(x['count']*x['size']),reverse=True)[:100]
    return {'path':str(root),'exists':True,'files':len(files),'bytes':sum(r['size'] for r in files),
            'file_records':files,'errors':errors[:200],
            'top_dirs':[{'name':k,'files':v['files'],'bytes':v['bytes']} for k,v in sorted(dir_stats.items(),key=lambda kv:kv[1]['bytes'],reverse=True)],
            'extensions':[{'ext':e,'files':n,'bytes':ext_bytes[e]} for e,n in sorted(ext_counts.items(),key=lambda kv:(-kv[1],kv[0]))],
            'top_files':top_files,'candidates':sorted(candidates,key=lambda x:x['size'],reverse=True)[:200],'duplicates':dup}

results=[scan_tree(t) for t in TARGETS]
# C root level-1/2 directory inventory (metadata only; recursive system dirs intentionally skipped)
croot=[]
try:
    for e in os.scandir('C:/'):
        try:
            if not e.is_dir(follow_symlinks=False): continue
            name=e.name
            item={'name':name,'path':e.path,'excluded_from_recursive_scan':name in EXCLUDE_ROOTS,'second_level':[]}
            try:
                for se in os.scandir(e.path):
                    try:
                        if se.is_dir(follow_symlinks=False): item['second_level'].append(se.name)
                    except Exception: pass
            except Exception as ex:
                item['second_level_error']=str(ex)
            item['second_level_count']=len(item['second_level'])
            croot.append(item)
        except Exception: pass
except Exception as ex:
    croot=[{'error':str(ex)}]
# User profile top-level inventory (metadata; helps show distribution and system/profile paths)
profile=[]
try:
    for e in os.scandir(r'C:\Users\Lenovo'):
        try:
            st=e.stat()
            profile.append({'name':e.name,'path':e.path,'is_dir':e.is_dir(follow_symlinks=False),'bytes':st.st_size if e.is_file(follow_symlinks=False) else None})
        except Exception: pass
except Exception as ex: profile=[{'error':str(ex)}]
# Aggregate all target files for cross-target stats
total_files=[]
for x in results: total_files.extend(x['file_records'])
all_ext=Counter(r['ext'] for r in total_files); all_ext_bytes=defaultdict(int)
for r in total_files: all_ext_bytes[r['ext']]+=r['size']
all_groups=defaultdict(list)
for r in total_files: all_groups[(r['name'].lower(),r['size'])].append(r['path'])
all_dups=[{'name':k[0],'size':k[1],'paths':v[:30],'count':len(v)} for k,v in all_groups.items() if len(v)>1]
all_dups=sorted(all_dups,key=lambda x:x['count']*x['size'],reverse=True)[:200]
# disk usage
volume={}
try:
    st=os.statvfs('C:/')
    volume={'total_bytes':st.f_frsize*st.f_blocks,'free_bytes':st.f_frsize*st.f_bavail,'used_bytes':st.f_frsize*(st.f_blocks-st.f_bfree)}
except Exception:
    pass
report={'generated_at':time.strftime('%Y-%m-%d %H:%M:%S %z'), 'targets':results,
        'aggregate':{'files':len(total_files),'bytes':sum(r['size'] for r in total_files),
                     'extensions':[{'ext':e,'files':n,'bytes':all_ext_bytes[e]} for e,n in sorted(all_ext.items(),key=lambda kv:(-kv[1],kv[0]))],
                     'top_files':sorted(total_files,key=lambda x:x['size'],reverse=True)[:100],
                     'duplicates':all_dups},
        'c_root':croot,'profile_top_level':profile,'volume':volume,
        'exclusions':sorted(EXCLUDE_ROOTS)}
# remove raw records from report to keep json manageable? retain for diagnostics but write separate compressed-ish JSON; keep all records for parent audit.
json_path=Path(r'D:\Users\Lenovo\Documents\ChatGPT\我的电脑\local_inventory_report.json')
json_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# markdown
md=[]
md.append(f"# 本地文件只读扫描报告\n\n生成时间：{report['generated_at']}\n\n扫描范围：`C:\\Users\\Lenovo\\Documents`、`Desktop`、`Downloads`；另列出 `C:\\` 一级/二级目录和用户配置目录。未递归扫描 Windows、Program Files、ProgramData 等系统目录。\n")
if volume:
    md.append(f"C 盘容量（系统统计）：总计 {human(volume['total_bytes'])}，已用 {human(volume['used_bytes'])}，可用 {human(volume['free_bytes'])}。\n")
md.append('## 1. 目录分布与占用\n')
for x in results:
    md.append(f"- `{x['path']}`：{x['files']:,} 个文件，{human(x['bytes'])}。")
    for d in x['top_dirs'][:20]: md.append(f"  - `{d['name']}`：{d['files']:,} 个文件，{human(d['bytes'])}")
md.append('\n## 2. 文件类型统计（扫描范围合计）\n')
for e,n in sorted(all_ext.items(),key=lambda kv:(-all_ext_bytes[kv[0]],kv[0]))[:80]: md.append(f"- `{e}`：{n:,} 个，{human(all_ext_bytes[e])}")
md.append('\n## 3. 最大文件（前 30）\n')
for r in sorted(total_files,key=lambda x:x['size'],reverse=True)[:30]: md.append(f"- {human(r['size'])} — `{r['path']}`")
md.append('\n## 4. 临时/缓存/备份样候选（只建议人工复核）\n')
all_candidates=[]
for x in results: all_candidates.extend(x['candidates'])
for r in sorted(all_candidates,key=lambda x:x['size'],reverse=True)[:100]: md.append(f"- {human(r['size'])} — `{r['path']}`（{r['reason']}，{r['age_days']} 天前修改）")
if not all_candidates: md.append('- 未发现匹配常见临时/缓存模式的文件。')
md.append('\n## 5. 疑似重复（同名且同大小，需人工确认内容）\n')
for g in all_dups[:100]: md.append(f"- `{g['name']}`，{human(g['size'])}，{g['count']} 份："+'；'.join(f'`{p}`' for p in g['paths']))
if not all_dups: md.append('- 未发现同名同大小重复组。')
md.append('\n## 6. C 盘根目录一级/二级目录（元数据清单）\n')
for d in sorted(croot,key=lambda x:x.get('name','').lower()):
    if 'error' in d: continue
    flag='（跳过递归扫描）' if d['excluded_from_recursive_scan'] else ''
    subs='、'.join(d['second_level'][:30])
    if len(d['second_level'])>30: subs += '…'
    md.append(f"- `{d['name']}` {flag}：二级目录 {d['second_level_count']} 个" + (f"（{subs}）" if subs else ''))
md.append('\n## 7. 明确不要直接移动/删除的路径\n')
md.append('- `C:\\Windows`、`C:\\Program Files`、`C:\\Program Files (x86)`、`C:\\ProgramData`、`C:\\System Volume Information`、`C:\\$Recycle.Bin`、`C:\\Recovery`、`C:\\Users\\Lenovo\\AppData`、`C:\\Users\\Lenovo\\NTUSER.DAT` 及其日志。它们可能影响系统、应用或用户配置。')
md.append('- 扫描中列出的“候选”仅表示模式匹配，不能据此自动删除；浏览器/开发工具缓存、日志和下载中的安装包可能仍在使用。')
md_path=Path(r'D:\Users\Lenovo\Documents\ChatGPT\我的电脑\local_inventory_report.md')
md_path.write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'json':str(json_path),'markdown':str(md_path),'targets':[(x['path'],x['files'],x['bytes'],len(x['errors'])) for x in results],'aggregate_files':len(total_files),'aggregate_bytes':sum(r['size'] for r in total_files),'croot_dirs':len(croot),'candidate_count':len(all_candidates),'duplicate_groups':len(all_dups),'volume':volume},ensure_ascii=False))

