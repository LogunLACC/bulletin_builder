# PowerShell pre-commit hook: runs spot-fix on staged HTML files, re-adds them, then runs email_guard
$ErrorActionPreference = 'Stop'
# Ensure we run from repo root
Set-Location -Path (git rev-parse --show-toplevel)

# Get staged html files
$changed = git diff --cached --name-only -- '*.html' 2>$null
if (-not $changed) { exit 0 }
$files = $changed -split "\r?\n" | Where-Object { $_ -and (Test-Path $_) }
if (-not $files) { exit 0 }

# Run spot-fix script on the staged files (script accepts multiple paths)
Write-Host "Running spot-fix on staged HTML files: $($files -join ', ')"
python tools/spot_fix_email_html.py @($files) | Out-Null

# Re-add any modified files
git add @($files)

# Run email guard on changed files (narrow to exports by default)
python tools/email_guard.py --changed-only --include "exports/**" --exclude "user_drafts/**" --exclude "tmp/**"
if ($LASTEXITCODE -ne 0) { Write-Error 'email_guard failed' ; exit 1 }

exit 0
