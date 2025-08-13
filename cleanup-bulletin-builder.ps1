param(
  [switch]$Apply,         # actually delete
  [switch]$PreferSrc      # if your canonical package is src\bulletin_builder
)

$ErrorActionPreference = "Stop"

# Robust script root detection
$root = $PSScriptRoot
if (-not $root -or $root -eq "") {
  if ($MyInvocation.MyCommand.Path) {
    $root = [System.IO.Path]::GetDirectoryName($MyInvocation.MyCommand.Path)
  } else {
    $root = (Get-Location).Path
  }
}


# Logging setup
$logFile = Join-Path $root 'cleanup.log'
function Write-Log {
  param([string]$Message)
  $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  $entry = "[$timestamp] $Message"
  Add-Content -Path $logFile -Value $entry
}

Write-Host "== Bulletin Builder Cleanup =="
Write-Host "Root: $root"
Write-Host ("Mode: {0}" -f ($(if ($Apply) {"APPLY"} else {"DRY-RUN"})))
Write-Log "--- Bulletin Builder Cleanup Run ---"
Write-Log "Root: $root"
Write-Log ("Mode: {0}" -f ($(if ($Apply) {"APPLY"} else {"DRY-RUN"})))

# Detect canonical package directory
$pkgTop = Join-Path $root 'bulletin_builder'
$pkgSrc = Join-Path $root 'src\bulletin_builder'

$hasTop = Test-Path -LiteralPath $pkgTop
$hasSrc = Test-Path -LiteralPath $pkgSrc


if (-not $hasTop -and -not $hasSrc) {
  Write-Log "ERROR: Cannot find 'bulletin_builder' under repo root or 'src/'. Aborting for safety."
  throw "Cannot find 'bulletin_builder' under repo root or 'src/'. Aborting for safety."
}

# Pick canonical (default: top-level; override with -PreferSrc)
if ($PreferSrc -and $hasSrc) {
  $keep = $pkgSrc
} elseif ($hasTop) {
  $keep = $pkgTop
} else {
  $keep = $pkgSrc
}
Write-Host "Canonical package: $keep"
Write-Log "Canonical package: $keep"

# Build deletion list
$toDelete = New-Object System.Collections.Generic.List[string]

# 1) Junk and caches
$junkDirs = @('build','dist','.pytest_cache','.mypy_cache','.ruff_cache','.eggs','.idea','.vscode','.venv','venv','env')
$junkFiles = @('.coverage','.DS_Store')

$eggInfo  = Get-ChildItem -LiteralPath $root -Filter '*.egg-info' -Directory -Recurse -ErrorAction SilentlyContinue
$pycache  = Get-ChildItem -LiteralPath $root -Directory -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq '__pycache__' }
$pyc      = Get-ChildItem -LiteralPath $root -Filter '*.pyc' -File -Recurse -ErrorAction SilentlyContinue

foreach ($d in $junkDirs) {
  $full = Join-Path $root $d
  if (Test-Path -LiteralPath $full) { [void]$toDelete.Add($full) }
}
foreach ($f in $junkFiles) {
  $hits = Get-ChildItem -LiteralPath $root -Filter $f -File -Recurse -ErrorAction SilentlyContinue
  foreach ($h in $hits) { [void]$toDelete.Add($h.FullName) }
}
foreach ($x in $eggInfo)  { [void]$toDelete.Add($x.FullName) }
foreach ($x in $pycache)  { [void]$toDelete.Add($x.FullName) }
foreach ($x in $pyc)      { [void]$toDelete.Add($x.FullName) }

# 2) Duplicate/legacy dirs at repo root (only if canonical has them)
$legacyCandidates = @('app_core','ui','bulletin_builder')  # last one handles stray duplicate package
foreach ($cand in $legacyCandidates) {
  $topCand = Join-Path $root $cand
  if (-not (Test-Path -LiteralPath $topCand)) { continue }

  if ($cand -eq 'bulletin_builder') {
    # If both top-level and src versions exist, delete the non-canonical
    if ($hasTop -and $hasSrc) {
      if ($keep -eq $pkgTop) { [void]$toDelete.Add($pkgSrc) } else { [void]$toDelete.Add($pkgTop) }
    }
  } else {
    # app_core or ui at repo root are duplicates if canonical pkg has them inside
    $inside = Join-Path $keep $cand
    if (Test-Path -LiteralPath $inside) { [void]$toDelete.Add($topCand) }
  }
}

# 3) De-dup and filter to existing paths
$final = $toDelete | Sort-Object -Unique | Where-Object { Test-Path -LiteralPath $_ }


if ($final.Count -eq 0) {
  Write-Host "Nothing to delete. (Either you're already tidy, or canonical paths differ.)"
  Write-Host "Tip: re-run with -PreferSrc if your live package is under src\bulletin_builder."
  Write-Log "Nothing to delete. (Either already tidy, or canonical paths differ.)"
  exit 0
}


Write-Host "`nWill remove the following paths:"
Write-Log "Paths to be deleted:"
foreach ($p in $final) {
  $rel = $p
  $prefix = $root + [IO.Path]::DirectorySeparatorChar
  if ($p.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    $rel = $p.Substring($prefix.Length)
  }
  Write-Host ("  - {0}" -f $rel)
  Write-Log ("  - {0}" -f $rel)
}


if (-not $Apply) {
  Write-Host "`n(DRY-RUN) Run with:  powershell -ExecutionPolicy Bypass -File .\cleanup-bulletin-builder.ps1 -Apply"
  Write-Log "DRY-RUN: No files deleted."
  exit 0
}


Write-Host "`nDeleting..."
Write-Log "Deleting the following paths:"
foreach ($p in $final) {
  if (Test-Path -LiteralPath $p -PathType Container) {
    Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue
    Write-Log "Deleted directory: $p"
  } else {
    Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
    Write-Log "Deleted file: $p"
  }
}
Write-Host "✅ Done."
Write-Log "✅ Done."
