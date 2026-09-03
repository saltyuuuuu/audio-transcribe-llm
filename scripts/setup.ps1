param(
  [string]$ArkApiKey = "",
  [string]$TextApiKey = "",
  [string]$TextBaseUrl = "",
  [string]$TextModel = "",
  [switch]$Force,
  [switch]$NoVenv,
  [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$ArgsList = @()

if ($ArkApiKey) { $ArgsList += @("--ark-api-key", $ArkApiKey) }
if ($TextApiKey) { $ArgsList += @("--text-api-key", $TextApiKey) }
if ($TextBaseUrl) { $ArgsList += @("--text-base-url", $TextBaseUrl) }
if ($TextModel) { $ArgsList += @("--text-model", $TextModel) }
if ($Force) { $ArgsList += "--force" }
if ($NoVenv) { $ArgsList += "--no-venv" }
if ($SkipInstall) { $ArgsList += "--skip-install" }

Set-Location $Root
python "$Root\scripts\setup.py" @ArgsList

