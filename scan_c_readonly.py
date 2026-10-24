import argparse
import datetime as dt
import json
import os
import re
import stat as statmod
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


def iso(ts):
    if ts is None:
        return None
    try:
        return dt.datetime.fromtimestamp(ts).astimezone().isoformat()
    except Exception:
        return None


def fmt_bytes(n):
    n = float(n)
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    for u in units:
        if abs(n) < 1024 or u == units[-1]:
            return f"{n:,.2f} {u}"
        n /= 1024


def ext_for(name):
    # Keep compound common package/archive suffixes useful in reports.
    lower = name.lower()
    for compound in (".tar.gz", ".tar.bz2", ".tar.xz", ".d.ts"):
        if lower.endswith(compound):
            return compound
    ext = Path(name).suffix.lower()
    return ext if ext else "[no extension]"


def safe_rel(path):
    try:
        return os.path.relpath(path, "C:\\").replace("/", "\\")
    except Exception:
        return path


def classify_path(path, name):
    s = (path + "\\" + name).lower()
    n = name.lower()
    labels = []
    patterns = (
        ("temporary", ("\\temp\\", "\\tmp\\", ".tmp", ".temp", "~$", "\\appdata\\local\\temp\\")),
        ("cache", ("\\cache\\", "\\caches\\", "\\__pycache__\\", "\\.npm\\", "\\.nuget\\", "\\pip\\cache\\")),
        ("history/checkpoint", ("\\.ipynb_checkpoints\\", ".bak", ".old", ".orig", ".save", ".swp")),
        ("logs/dumps", (".log", ".dmp", ".etl", "\\logs\\")),
        ("recycle-bin", ("$recycle.bin",)),
        ("installer/update residue", (".msi", ".msp", "\\softwaredistribution\\download\\", "windows.old", "$windows.~bt")),
        ("development artifact", ("\\node_modules\\", "\\bin\\debug\\", "\\bin\\release\\", "\\obj\\", "\\dist\\", "\\build\\")),
    )
    for label, pats in patterns:
        if any(p in s or p in n for p in pats):
            labels.append(label)
    return labels


def scan_tree(root, now):
    dirs = {}
    files = []
    ext = Counter()
    ext_bytes = Counter()
    categories = Counter()
    errors = []
    skipped_reparse = []
    stack = [os.path.abspath(root)]
    visited = set()
    last_progress = time.monotonic()
    dirs_seen = 0
    files_seen = 0
    total_bytes = 0
    age_buckets = Counter()

    def init_dir(path):
        if path not in dirs:
            parent = os.path.dirname(path.rstrip("\\"))
            dirs[path] = {
                "path": path,
                "relative": safe_rel(path),
                "parent": parent if parent != path else None,
                "depth": safe_rel(path).count("\\") if safe_rel(path) != "." else 0,
                "direct_file_count": 0,
                "direct_file_bytes": 0,
                "direct_child_dir_count": 0,
                "recursive_file_count": 0,
                "recursive_bytes": 0,
                "last_modified_epoch": None,
                "classification": [],
            }
        return dirs[path]

    init_dir(os.path.abspath(root))
    while stack:
        dpath = stack.pop()
        if dpath in visited:
            continue
        visited.add(dpath)
        dinfo = init_dir(dpath)
        try:
            entries = os.scandir(dpath)
        except (PermissionError, OSError) as e:
            errors.append({"path": dpath, "kind": "directory", "error": repr(e)})
            continue
        try:
            for entry in entries:
                ep = entry.path
                try:
                    st = entry.stat(follow_symlinks=False)
                except (PermissionError, OSError) as e:
                    errors.append({"path": ep, "kind": "entry_stat", "error": repr(e)})
                    continue
                attrs = getattr(st, "st_file_attributes", 0)
                is_reparse = bool(attrs & getattr(statmod, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
                try:
                    is_dir = entry.is_dir(follow_symlinks=False)
                except OSError:
                    is_dir = False
                if is_dir:
                    dinfo["direct_child_dir_count"] += 1
                    child = init_dir(ep)
                    child["last_modified_epoch"] = st.st_mtime
                    child["classification"] = classify_path(dpath, entry.name)
                    if is_reparse:
                        skipped_reparse.append({"path": ep, "kind": "directory_reparse_point"})
                    else:
                        stack.append(ep)
                    continue
                # Reparse-point files are still counted as files but never followed.
                try:
                    size = int(st.st_size)
                except Exception:
                    size = 0
                mtime = st.st_mtime
                atime = st.st_atime
                ctime = st.st_ctime
                labels = classify_path(dpath, entry.name)
                for label in labels:
                    categories[label] += 1
                ex = ext_for(entry.name)
                ext[ex] += 1
                ext_bytes[ex] += size
                age_days = max(0, (now - mtime) / 86400.0)
                if age_days >= 365:
                    bucket = ">=1 year"
                elif age_days >= 180:
                    bucket = "180-364 days"
                elif age_days >= 90:
                    bucket = "90-179 days"
                elif age_days >= 30:
                    bucket = "30-89 days"
                else:
                    bucket = "<30 days"
                age_buckets[bucket] += 1
                item = {
                    "path": ep,
                    "relative": safe_rel(ep),
                    "name": entry.name,
                    "parent": dpath,
                    "size": size,
                    "size_human": fmt_bytes(size),
                    "extension": ex,
                    "created": iso(getattr(st, "st_ctime", None)),
                    "modified": iso(mtime),
                    "accessed": iso(atime),
                    "modified_epoch": mtime,
                    "accessed_epoch": atime,
                    "age_days_since_modified": round(age_days, 1),
                    "age_days_since_access": round(max(0, (now - atime) / 86400.0), 1),
                    "classification": labels,
                    "reparse_point": is_reparse,
                }
                files.append(item)
                dinfo["direct_file_count"] += 1
                dinfo["direct_file_bytes"] += size
                dinfo["last_modified_epoch"] = max(dinfo["last_modified_epoch"] or 0, mtime)
                total_bytes += size
                files_seen += 1
                if time.monotonic() - last_progress > 15:
                    print(f"progress: dirs={len(visited):,} files={files_seen:,} bytes={fmt_bytes(total_bytes)}", file=sys.stderr, flush=True)
                    last_progress = time.monotonic()
        finally:
            entries.close()
        dirs_seen += 1

    # Roll direct statistics up to parents to obtain recursive directory sizes.
    by_depth = sorted(dirs.values(), key=lambda x: x["depth"], reverse=True)
    for info in by_depth:
        info["recursive_file_count"] = info["direct_file_count"]
        info["recursive_bytes"] = info["direct_file_bytes"]
        p = info["parent"]
        if p in dirs and p != info["path"]:
            dirs[p]["recursive_file_count"] += info["recursive_file_count"]
            dirs[p]["recursive_bytes"] += info["recursive_bytes"]

    for info in dirs.values():
        info["recursive_bytes_human"] = fmt_bytes(info["recursive_bytes"])
        info["direct_file_bytes_human"] = fmt_bytes(info["direct_file_bytes"])
        info["last_modified"] = iso(info["last_modified_epoch"])
        info.pop("last_modified_epoch", None)

    # Make a bounded list of high-signal candidates; full file metadata remains in JSON.
    stale = [f for f in files if f["age_days_since_modified"] >= 365]
    stale.sort(key=lambda x: (x["size"], x["age_days_since_modified"]), reverse=True)
    classified = [f for f in files if f["classification"]]
    classified.sort(key=lambda x: (x["size"], x["age_days_since_modified"]), reverse=True)
    shallow = [f for f in files if f["relative"].count("\\") <= 2]
    shallow.sort(key=lambda x: x["size"], reverse=True)
    return {
        "root": root,
        "files": files,
        "directories": list(dirs.values()),
        "errors": errors,
        "skipped_reparse_points": skipped_reparse,
        "extension_counts": dict(ext.most_common()),
        "extension_bytes": {k: {"bytes": v, "human": fmt_bytes(v)} for k, v in ext_bytes.most_common()},
        "classification_counts": dict(categories),
        "age_buckets": dict(age_buckets),
        "stale_candidates_top": stale[:300],
        "classified_candidates_top": classified[:300],
        "shallow_scattered_candidates": shallow[:300],
        "totals": {
            "file_count": len(files),
            "directory_count": len(dirs),
            "total_file_bytes": total_bytes,
            "total_file_bytes_human": fmt_bytes(total_bytes),
        },
    }


def registry_software():
    # Read only. Registry is optional on non-Windows or if a key is inaccessible.
    try:
        import winreg
    except Exception as e:
        return {"error": repr(e), "software": []}
    software = []
    errors = []
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "HKLM 64-bit"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall", "HKLM 32-bit"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "HKCU"),
    ]
    fields = ["DisplayName", "DisplayVersion", "Publisher", "InstallLocation", "InstallDate", "UninstallString", "EstimatedSize"]
    for hive, path, view in roots:
        try:
            key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
        except OSError as e:
            errors.append({"key": view + "\\" + path, "error": repr(e)})
            continue
        try:
            count = winreg.QueryInfoKey(key)[0]
            for i in range(count):
                try:
                    sub = winreg.EnumKey(key, i)
                    sk = winreg.OpenKey(key, sub, 0, winreg.KEY_READ)
                    row = {"registry_view": view, "key": path + "\\" + sub}
                    for field in fields:
                        try:
                            row[field] = winreg.QueryValueEx(sk, field)[0]
                        except OSError:
                            row[field] = None
                    if row.get("DisplayName"):
                        software.append(row)
                    winreg.CloseKey(sk)
                except OSError as e:
                    errors.append({"key": view + "\\" + path, "index": i, "error": repr(e)})
        finally:
            winreg.CloseKey(key)
    dedup = {}
    for row in software:
        ident = (row.get("DisplayName"), row.get("DisplayVersion"), row.get("InstallLocation"), row.get("Publisher"))
        dedup[ident] = row
    return {"software": sorted(dedup.values(), key=lambda x: (str(x.get("DisplayName")), str(x.get("DisplayVersion")))), "errors": errors}


def write_reports(result, out_md, out_json, started, ended, disk):
    result["scan"] = {
        "started": iso(started),
        "ended": iso(ended),
        "duration_seconds": round(ended - started, 2),
        "read_only": True,
        "file_contents_opened": False,
        "scope": "C:\\ recursively, excluding traversal into reparse-point directories",
    }
    result["disk_usage_at_scan"] = {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "total_human": fmt_bytes(disk.total),
        "used_human": fmt_bytes(disk.used),
        "free_human": fmt_bytes(disk.free),
    }
    result["installed_software"] = registry_software()
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    totals = result["totals"]
    dirs = result["directories"]
    exts = result["extension_counts"]
    extbytes = result["extension_bytes"]
    age = result["age_buckets"]
    cls = result["classification_counts"]
    sw = result["installed_software"].get("software", [])
    top_dirs = sorted(dirs, key=lambda x: x["recursive_bytes"], reverse=True)
    root_children = [d for d in dirs if d.get("parent") == "C:\\"]
    root_children.sort(key=lambda x: x["recursive_bytes"], reverse=True)
    lines = []
    lines.append("# C: 盘只读扫描报告\n")
    lines.append("> 生成时间：%s ；扫描范围：`C:\\` 递归目录项和元数据。\n> 本报告仅读取目录项、文件大小/时间/扩展名和注册表软件信息；没有打开任何文件内容，也没有移动、删除、重命名或修改系统。\n" % result["scan"]["ended"])
    lines.append("## 1. 扫描概况\n")
    lines.append(f"- 文件：**{totals['file_count']:,}**；目录：**{totals['directory_count']:,}**；文件合计：**{totals['total_file_bytes_human']}**（按文件大小求和）")
    lines.append(f"- C: 盘容量：{result['disk_usage_at_scan']['total_human']}；已用：{result['disk_usage_at_scan']['used_human']}；可用：{result['disk_usage_at_scan']['free_human']}")
    lines.append(f"- 扫描耗时：{result['scan']['duration_seconds']} 秒；权限/读取错误：{len(result['errors']):,}；跳过的重解析点：{len(result['skipped_reparse_points']):,}")
    lines.append("\n## 2. 顶层目录占用（递归）\n")
    lines.append("|目录|文件数|占用|直接文件数|备注|\n|---|---:|---:|---:|---|")
    for d in root_children:
        lines.append(f"|`{d['path']}`|{d['recursive_file_count']:,}|{d['recursive_bytes_human']}|{d['direct_file_count']:,}|{', '.join(d['classification']) or ''}|")
    lines.append("\n## 3. 最大目录（递归占用 Top 200）\n")
    lines.append("|目录|文件数|递归占用|直接文件数|\n|---|---:|---:|---:|")
    for d in top_dirs[:200]:
        lines.append(f"|`{d['path']}`|{d['recursive_file_count']:,}|{d['recursive_bytes_human']}|{d['direct_file_count']:,}|")
    lines.append("\n完整目录清单（含每个目录的递归文件数、递归大小、直接文件数）在 JSON 的 `directories` 字段中。\n")
    lines.append("## 4. 文件类型分布\n")
    lines.append("|扩展名|文件数|大小|\n|---|---:|---:|")
    for e, count in list(exts.items())[:200]:
        lines.append(f"|`{e}`|{count:,}|{extbytes[e]['human']}|")
    lines.append("\n## 5. 按修改时间的年龄分布\n")
    lines.append("|距最后修改|文件数|\n|---|---:|")
    for b in ["<30 days", "30-89 days", "90-179 days", "180-364 days", ">=1 year"]:
        lines.append(f"|{b}|{age.get(b, 0):,}|")
    lines.append("\n> 修改时间只能说明长期未修改，不能证明文件没有使用；删除前应人工确认。\n")
    lines.append("## 6. 可人工复核的候选项（不执行任何清理）\n")
    lines.append("下列项目只按命名模式或修改时间筛选，**不是删除建议**。完整列表分别在 JSON 的 `stale_candidates_top`、`classified_candidates_top`、`shallow_scattered_candidates`。\n")
    lines.append("### 6.1 超过 1 年未修改且体积较大的文件（Top 100）\n")
    lines.append("|文件|大小|最后修改|最后访问|分类|\n|---|---:|---|---|---|")
    for f in result["stale_candidates_top"][:100]:
        lines.append(f"|`{f['path']}`|{f['size_human']}|{f['modified']}|{f['accessed']}|{', '.join(f['classification'])}|")
    lines.append("\n### 6.2 临时、缓存、日志、备份、开发产物等命名模式（Top 100）\n")
    lines.append("|文件|大小|最后修改|分类|\n|---|---:|---|---|")
    for f in result["classified_candidates_top"][:100]:
        lines.append(f"|`{f['path']}`|{f['size_human']}|{f['modified']}|{', '.join(f['classification'])}|")
    lines.append("\n### 6.3 根目录及浅层散落文件（Top 100）\n")
    lines.append("|文件|大小|最后修改|扩展名|\n|---|---:|---|---|")
    for f in result["shallow_scattered_candidates"][:100]:
        lines.append(f"|`{f['path']}`|{f['size_human']}|{f['modified']}|`{f['extension']}`|")
    lines.append("\n## 7. 命名模式统计\n")
    lines.append("|模式|文件数|\n|---|---:|")
    for k, v in sorted(cls.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"|{k}|{v:,}|")
    lines.append("\n## 8. 已安装软件（注册表只读）\n")
    lines.append(f"共读取到 **{len(sw):,}** 条去重后的卸载注册表项；软件清单含名称、版本、发布者、安装位置等字段，完整数据在 JSON 的 `installed_software.software`。\n")
    lines.append("|名称|版本|发布者|安装位置|注册表视图|\n|---|---|---|---|---|")
    for row in sw:
        def cell(v):
            return str(v or "").replace("|", "\\|").replace("\n", " ")
        lines.append(f"|{cell(row.get('DisplayName'))}|{cell(row.get('DisplayVersion'))}|{cell(row.get('Publisher'))}|`{cell(row.get('InstallLocation'))}`|{cell(row.get('registry_view'))}|")
    lines.append("\n## 9. 权限错误和扫描边界\n")
    lines.append("遇到无权限目录/条目时已记录并继续；错误详情在 JSON 的 `errors`。重解析点（junction/symlink 等）没有递归跟进，以避免重复扫描或跨盘循环，路径在 `skipped_reparse_points`。\n")
    lines.append("## 10. 使用建议\n")
    lines.append("先在候选列表中按路径、所有者、关联软件和备份情况逐项确认。`Temp`、缓存、日志、回收站和更新残留有时仍被程序使用；系统目录、`Program Files`、`ProgramData`、`Windows`、`AppData`、用户配置文件不要直接删除。需要清理时应使用 Windows 设置中的存储/磁盘清理或对应软件自身的卸载/清理功能，并在另一步获得明确授权后执行。\n")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    started = time.time()
    now = time.time()
    disk = __import__("shutil").disk_usage("C:\\")
    result = scan_tree("C:\\", now)
    ended = time.time()
    write_reports(result, os.path.join(out_dir, "scan_C_report.md"), os.path.join(out_dir, "scan_C_report.json"), started, ended, disk)
    print(f"wrote {os.path.join(out_dir, 'scan_C_report.md')}")
    print(f"wrote {os.path.join(out_dir, 'scan_C_report.json')}")
    print(json.dumps({"totals": result["totals"], "errors": len(result["errors"]), "skipped_reparse": len(result["skipped_reparse_points"]), "software": len(result["installed_software"]["software"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
