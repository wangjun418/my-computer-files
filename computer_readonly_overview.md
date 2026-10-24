# 电脑全盘只读结构总览

生成时间：2026-10-24（Asia/Shanghai）

本次只读取 C:\、D:\、E:\ 的目录项、文件大小、扩展名和时间元数据，并读取 Windows 卸载注册表的软件项。没有打开文件内容，没有移动、删除、重命名，没有清理缓存，也没有修改系统。

## 卷与覆盖范围

|盘符|文件|目录|文件大小合计|卷已用|卷可用|访问错误|跳过重解析点|
|---|---:|---:|---:|---:|---:|---:|---:|
|C:|933,303|287,550|142.03 GiB|164.79 GiB|35.21 GiB|125|61|
|D:|751,001|83,426|319.87 GiB|318.50 GiB|55.65 GiB|6|0|
|E:|120,442|21,120|237.52 GiB|237.35 GiB|140.15 GiB|2|0|

C/D/E 是当前机器列出的固定文件卷；另一个 `Temp` 项只是 C:\Users\Lenovo\AppData\Local\Temp 的 PowerShell 别名，不是独立磁盘。

## 主要结构

### C:

- 主要空间来自 Windows/Office/驱动、用户 AppData 缓存、浏览器/微信/飞书/WPS/豆包缓存、开发工具和 Claude/Codex 运行时。
- 大目录例子：BaiduYunKernel 加速缓存约 2.57 GiB、Windows System32 约 2.43 GiB、Windows Installer 约 1.99 GiB、屏幕录制约 1.20 GiB、金山备份约 1.05 GiB、豆包/Kimi/微信/飞书缓存多处数百 MiB。
- 修改时间分布：30 天内 164,133 个；30–89 天 82,504 个；90–179 天 76,349 个；180–364 天 341,428 个；超过 1 年 268,889 个。
- 文件类型中体积较大的是 DLL 35.32 GiB、无扩展名 28.57 GiB、EXE 13.17 GiB、PDF 4.09 GiB、JS 1.86 GiB、LOG 1.89 GiB。
- 注册表读取到 97 条去重软件项。完整软件表在 C 盘报告第 8 节，包含版本、发布者、安装位置和注册表视图。

### D:

- 回收站 `D:\$RECYCLE.BIN\...` 约 37.55 GiB，是最大的单项。
- `信息部网盘` 的考研课程视频多个目录合计占用很大；根目录散落文件约 15.69 GiB；`app` 约 12.08 GiB；`软件` 约 7.84 GiB。
- TeX Live 归档存在 3 份约 5.53 GiB 的大目录：`软件\texlive2025\archive`、`app\texlive2025 (1)\archive`、`app\texlive\archive`，需要人工确认是否为重复安装/备份。
- 长期未修改大文件候选包括 `R2024a_Update_3_Windows.iso`（12.53 GiB）、SPSS 安装压缩包（1.01 GiB）、`教材.zip`（879.86 MiB）和 MATLAB 安装包。它们只被列为候选。

### E:

- `24年cfa一级网课双机构` 约 17.55 GB；`LeStoreDownload` 约 9.96 GB；英语六级课程多个目录各约 8–9 GB；微信文件/附件按月份积累。
- 类别占用：视频约 133.17 GiB（2,628 个）；可执行/安装包约 18.63 GiB（1,356 个）；库/系统文件约 18.42 GiB；PDF 约 14.43 GiB；压缩包约 13.42 GiB；演示文稿约 13.19 GiB。
- 长期未修改候选包括 Photoshop 安装包（3.12 GiB、1.89 GiB）、CFA 课程视频、多年前的安装包，以及约 1 GiB 的 `.tmp` 文件；课程资料和安装包不能只凭日期删除。

## 可人工复核的类别

- **较明确的候选**：回收站内容、下载目录中的旧安装包、明确标记为 `.tmp`/`.downloading`/旧版本的安装残留、重复的安装介质和重复的 TeX Live 归档。
- **需人工判断**：课程视频、教材、论文/数据、微信/飞书聊天附件、Photoshop/MATLAB/SPSS/TeX Live 安装包、WPS/Anaconda/开发工具缓存。
- **不要直接触碰**：Windows、Program Files、ProgramData、AppData、WindowsApps、System Volume Information、pagefile/swapfile、驱动目录、DLL、Windows Installer、用户注册表文件、正在使用的软件目录。
- “长期未修改”只表示最后写入时间较早；Windows 访问时间可能关闭或不可靠，不能证明文件未使用。

## 详细报告与逐文件数据

- [C 盘报告](D:/Users/Lenovo/Documents/ChatGPT/我的电脑/scan_C_report.md) · [C 盘完整 JSON](D:/Users/Lenovo/Documents/ChatGPT/我的电脑/scan_C_report.json)
- [D 盘报告](D:/Users/Lenovo/Documents/ChatGPT/我的电脑/scan_D_report.md) · [D 盘完整 JSON](D:/Users/Lenovo/Documents/ChatGPT/我的电脑/scan_D_report.json)
- [E 盘报告](D:/Users/Lenovo/Documents/ChatGPT/我的电脑/scan_E_report.md) · [E 盘完整 JSON](D:/Users/Lenovo/Documents/ChatGPT/我的电脑/scan_E_report.json) · [E 盘逐文件 JSONL](D:/Users/Lenovo/Documents/ChatGPT/我的电脑/scan_E_file_metadata.jsonl)

本总览和三份分盘报告均为只读检查结果；没有执行清理。
