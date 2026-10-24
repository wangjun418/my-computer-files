# 本地文件只读扫描报告

生成时间：2026-10-24 12:27:00 +0800

扫描范围：`C:\Users\Lenovo\Documents`、`Desktop`、`Downloads`；另列出 `C:\` 一级/二级目录和用户配置目录。未递归扫描 Windows、Program Files、ProgramData 等系统目录。

## 1. 目录分布与占用

- `C:\Users\Lenovo\Documents`：5 个文件，12.49 MB。
  - `kimi`：2 个文件，12.45 MB
  - `Codex`：3 个文件，36.97 KB
- `C:\Users\Lenovo\Desktop`：0 个文件，0.00 B。
- `C:\Users\Lenovo\Downloads`：4 个文件，129.91 MB。
  - `claude-code-cli`：2 个文件，129.40 MB
  - `(root)`：1 个文件，526.29 KB
  - `.ipynb_checkpoints`：1 个文件，72.00 B

## 2. 文件类型统计（扫描范围合计）

- `.tgz`：2 个，129.40 MB
- `.pdf`：1 个，12.39 MB
- `.ipynb`：2 个，526.37 KB
- `.jpg`：1 个，68.03 KB
- `.txt`：1 个，35.94 KB
- `.py`：2 个，1.03 KB

## 3. 最大文件（前 30）

- 129.37 MB — `C:\Users\Lenovo\Downloads\claude-code-cli\anthropic-ai-claude-code-win32-x64-2.1.310.tgz`
- 12.39 MB — `C:\Users\Lenovo\Documents\kimi\workspace\source_paper.pdf`
- 526.29 KB — `C:\Users\Lenovo\Downloads\Untitled.ipynb`
- 68.03 KB — `C:\Users\Lenovo\Documents\kimi\workspace\inspiration.jpg`
- 35.94 KB — `C:\Users\Lenovo\Documents\Codex\2026-08-31\new-chat\work\extracted_text.txt`
- 28.40 KB — `C:\Users\Lenovo\Downloads\claude-code-cli\anthropic-ai-claude-code-2.1.310.tgz`
- 624.00 B — `C:\Users\Lenovo\Documents\Codex\2026-08-31\new-chat\work\extract_docx_text.py`
- 430.00 B — `C:\Users\Lenovo\Documents\Codex\2026-08-31\new-chat\work\print_selected.py`
- 72.00 B — `C:\Users\Lenovo\Downloads\.ipynb_checkpoints\Untitled-checkpoint.ipynb`

## 4. 临时/缓存/备份样候选（只建议人工复核）

- 72.00 B — `C:\Users\Lenovo\Downloads\.ipynb_checkpoints\Untitled-checkpoint.ipynb`（cache/temp-like directory，413.9 天前修改）

## 5. 疑似重复（同名且同大小，需人工确认内容）

- 未发现同名同大小重复组。

## 6. C 盘根目录一级/二级目录（元数据清单）

- `$Recycle.Bin` （跳过递归扫描）：二级目录 4 个（S-1-5-18、S-1-5-21-116588299-1789807713-3781712828-1001、S-1-5-21-116588299-1789807713-3781712828-500、S-1-5-21-284080498-1770358539-2764220212-500）
- `$WINDOWS.~BT` ：二级目录 1 个（Sources）
- `common_attachment` ：二级目录 0 个
- `Documents and Settings` ：二级目录 0 个
- `inetpub` ：二级目录 0 个
- `KRECYCLE` ：二级目录 0 个
- `OneDriveTemp` ：二级目录 1 个（S-1-5-21-116588299-1789807713-3781712828-1001）
- `PdfConvert` ：二级目录 0 个
- `PerfLogs` （跳过递归扫描）：二级目录 0 个
- `Program Files` （跳过递归扫描）：二级目录 24 个（AMD、Common Files、Internet Explorer、Lenovo、Microsoft、Microsoft Office、Microsoft Office 15、Microsoft OfficePLUS、Microsoft OneDrive、Microsoft Update Health Tools、ModifiableWindowsApps、Nutstore、Tencent、Tesseract-OCR、Uninstall Information、Windows Defender、Windows Mail、Windows Media Player、Windows NT、Windows Photo Viewer、Windows Sidebar、WindowsApps、WindowsPowerShell、Zotero）
- `Program Files (x86)` （跳过递归扫描）：二级目录 21 个（Adobe、Common Files、Google、Internet Explorer、Kingsoft、Lenovo、MGTVPCC、Microsoft、Microsoft Office、Microsoft.NET、Mozilla Maintenance Service、QQMailPlugin、Tencent、Uninstall Information、Windows Defender、Windows Mail、Windows Media Player、Windows NT、Windows Photo Viewer、Windows Sidebar、WindowsPowerShell）
- `ProgramData` （跳过递归扫描）：二级目录 47 个（Adobe、Alibaba、AMD、Application Data、AxMath、boost_interprocess、CrossDevice、Documents、Dolby、fastpdf、Foxit Software、IBM、kdesk、kingsoft、Lenovo、Local、lx-ad-sdk、Microsoft、Microsoft Office、Microsoft OfficePLUS、Microsoft OneDrive、mwboost_interprocess、Nutstore、Oray、OrayClient、Package Cache、Packages、Propagation、regid.1991-06.com.microsoft、SafeNet Sentinel…）
- `Recovery` （跳过递归扫描）：二级目录 0 个
- `System Volume Information` （跳过递归扫描）：二级目录 0 个
- `texlive` ：二级目录 2 个（2025、texmf-local）
- `Users` ：二级目录 4 个（Default、Default User、Lenovo、Public）
- `Windows` （跳过递归扫描）：二级目录 85 个（appcompat、apppatch、AppReadiness、assembly、bcastdvr、Boot、Branding、BrowserCore、CbsTemp、Cursors、debug、diagnostics、DiagTrack、DigitalLocker、Downloaded Program Files、ELAMBKUP、en-US、favlinks、Firmware、Fonts、GameBarPresenceWriter、Globalization、Help、IdentityCRL、IME、ImmersiveControlPanel、InboxApps、INF、InputMethod、Installer…）

## 7. 明确不要直接移动/删除的路径

- `C:\Windows`、`C:\Program Files`、`C:\Program Files (x86)`、`C:\ProgramData`、`C:\System Volume Information`、`C:\$Recycle.Bin`、`C:\Recovery`、`C:\Users\Lenovo\AppData`、`C:\Users\Lenovo\NTUSER.DAT` 及其日志。它们可能影响系统、应用或用户配置。
- 扫描中列出的“候选”仅表示模式匹配，不能据此自动删除；浏览器/开发工具缓存、日志和下载中的安装包可能仍在使用。