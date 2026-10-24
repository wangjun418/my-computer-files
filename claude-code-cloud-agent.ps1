param([switch]$Probe)
$ErrorActionPreference = "Stop"
$claude = Join-Path $env:APPDATA "npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"
if (-not (Test-Path -LiteralPath $claude)) { throw "Claude Code executable not found: $claude" }
$settingsPath = Join-Path $env:USERPROFILE ".claude\settings.json"
$baseUrl = $null
if (Test-Path -LiteralPath $settingsPath) {
  try { $cfg = Get-Content -Raw -LiteralPath $settingsPath | ConvertFrom-Json; $baseUrl = $cfg.env.ANTHROPIC_BASE_URL } catch { }
}
$isOfficialApi = [string]::IsNullOrWhiteSpace($baseUrl) -or $baseUrl -match '^https://api\.anthropic\.com(?:/|$)'
$mode = if ($isOfficialApi) { "cloud" } else { "interactive" }
if ($Probe) { "mode=$mode`nbaseUrl=$baseUrl"; exit 0 }
Set-Location -LiteralPath (Join-Path $env:USERPROFILE "Documents")
if ($isOfficialApi) { & $claude --cloud } else { & $claude }
exit $LASTEXITCODE
