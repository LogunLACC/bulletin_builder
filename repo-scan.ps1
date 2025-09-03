<# 
Repo Scan – Windows PowerShell 5.1 compatible
Creates ./reports with JSON/text outputs and a master _summary.json.
Safe to run repeatedly; failures don’t stop the rest of the scan.

What it checks
- Git status
- Python: ruff, mypy, bandit, pip-audit, piplicenses, pytest (if tests), semgrep, detect-secrets
- Node: install, ESLint, TypeScript (if tsconfig), npm audit, depcheck, license-checker, tests (vitest/jest if present), semgrep, detect-secrets

Requirements
- Python 3.x in PATH (so `python` works)
- Node.js + npm in PATH (so `npm` and `npx` work)

Run
  Set-ExecutionPolicy -Scope Process Bypass -Force
  .\repo-scan.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Step($msg) { Write-Host "==> $msg" }
function TryRun($name, $scriptblock) {
  try {
    & $scriptblock
    return @{ name=$name; status="ok" }
  } catch {
    $msg = $_.Exception.Message
    Write-Warning "[$name] $_"
    return @{ name=$name; status="error"; error=$msg }
  }
}

# Prepare directories
$Root = Get-Location
$Reports = Join-Path $Root "reports"
if (-not (Test-Path $Reports)) { New-Item -ItemType Directory -Path $Reports | Out-Null }

# Detect stacks
$isNode = Test-Path (Join-Path $Root "package.json")
# Python detection: pyproject, requirements, or any .py file
$isPy = (Test-Path (Join-Path $Root "pyproject.toml")) -or (Test-Path (Join-Path $Root "requirements.txt")) -or `
        (Get-ChildItem -Recurse -Filter *.py -ErrorAction SilentlyContinue | Select-Object -First 1)

# Load package.json if present
$pkg = $null
if ($isNode) {
  TryRun "node:read-package" {
    $global:pkg = Get-Content package.json -Raw | ConvertFrom-Json
  } | Out-Null
}

$results = @()

# ------------------ General ------------------
Step "General: Git status & size"
$results += TryRun "git:status" { 
  $o = @{
    branch = (git rev-parse --abbrev-ref HEAD 2>$null)
    head   = (git rev-parse HEAD 2>$null)
    dirty  = ([bool](git status --porcelain 2>$null))
  }
  ($o | ConvertTo-Json -Depth 5) | Out-File -Encoding utf8 (Join-Path $Reports "git.json")
}

# ------------------ Python ------------------
if ($isPy) {
  Step "Python: installing tools (user site)"
  $results += TryRun "py:install-tools" {
    python -m pip install --user --upgrade pip > $Reports\pip-upgrade.log 2>&1
    python -m pip install --user ruff mypy bandit pip-audit detect-secrets semgrep pip-licenses pytest > $Reports\pip-tools-install.log 2>&1
  }

  Step "Python: Ruff (lint)"
  $results += TryRun "py:ruff" {
    python -m ruff check . --output-format json | Out-File -Encoding utf8 $Reports\ruff.json
  }

  Step "Python: mypy (types)"
  $results += TryRun "py:mypy" {
    python -m mypy . --pretty --show-error-codes --ignore-missing-imports | Out-File -Encoding utf8 $Reports\mypy.txt
  }

  Step "Python: Bandit (SAST)"
  $results += TryRun "py:bandit" {
    python -m bandit -r . -q -f json -o $Reports\bandit.json
  }

  Step "Python: dependency audit"
  $req = if (Test-Path ".\requirements.txt") { "-r .\requirements.txt" } else { "" }
  $results += TryRun "py:pip-audit" {
    if ($req -ne "") { python -m pip_audit $req --format json | Out-File -Encoding utf8 $Reports\pip-audit.json }
    else { python -m pip_audit --format json | Out-File -Encoding utf8 $Reports\pip-audit.json }
  }

  Step "Python: licenses"
  $results += TryRun "py:licenses" {
    python -m piplicenses --format=json --with-authors --with-urls | Out-File -Encoding utf8 $Reports\py-licenses.json
  }

  # Test discovery (PS 5.1 requires parentheses around each side of -or)
  $hasTests = $false
  $results += TryRun "py:detect-tests" {
    $existsTestsFolder = Test-Path -Path ".\tests"
    $existsTestFiles = Get-ChildItem -Path . -Include "test_*.py","*_test.py" -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if ( ($existsTestsFolder) -or ($existsTestFiles) ) { $script:hasTests = $true }
  }

  if ($hasTests) {
    Step "Python: pytest (smoke)"
    $results += TryRun "py:pytest" {
      python -m pytest -q | Out-File -Encoding utf8 $Reports\pytest.txt
    }
  } else {
    $results += @{ name="py:pytest"; status="skipped"; reason="no tests found" }
  }

  Step "Python: Semgrep (auto config)"
  $results += TryRun "py:semgrep" {
    python -m semgrep --config auto --json --error --timeout 120 > $Reports\semgrep.json
  }

  Step "Python: secrets scan"
  $results += TryRun "py:detect-secrets" {
    python -m detect_secrets scan --all-files > $Reports\detect-secrets.json
  }
} else {
  $results += @{ name="python"; status="skipped"; reason="no Python indicators" }
}

# ------------------ Node / TypeScript ------------------
if ($isNode) {
  Step "Node: install (lock-respecting)"
  $results += TryRun "node:install" {
    if (Test-Path "pnpm-lock.yaml") {
      # Prefer pnpm if lockfile exists; try via npx so we don't require global install
      npx --yes pnpm install --frozen-lockfile | Out-File -Encoding utf8 $Reports\node-install.txt
    } elseif (Test-Path "yarn.lock")  {
      npx --yes yarn install --frozen-lockfile | Out-File -Encoding utf8 $Reports\node-install.txt
    } elseif (Test-Path "package-lock.json") {
      npm ci | Out-File -Encoding utf8 $Reports\node-install.txt
    } else {
      npm install | Out-File -Encoding utf8 $Reports\node-install.txt
    }
  }

  Step "Node: ESLint"
  $results += TryRun "node:eslint" {
    npx --yes eslint . --ext .js,.jsx,.ts,.tsx -f json -o $Reports\eslint.json
  }

  if (Test-Path "tsconfig.json") {
    Step "Node: tsc (types)"
    $results += TryRun "node:tsc" {
      npx --yes tsc --noEmit | Out-File -Encoding utf8 $Reports\tsc.txt
    }
  } else {
    $results += @{ name="node:tsc"; status="skipped"; reason="no tsconfig.json" }
  }

  Step "Node: dependency audit"
  $results += TryRun "node:audit" {
    npm audit --json | Out-File -Encoding utf8 $Reports\npm-audit.json
  }

  Step "Node: depcheck (unused/missing)"
  $results += TryRun "node:depcheck" {
    npx --yes depcheck | Out-File -Encoding utf8 $Reports\depcheck.txt
  }

  Step "Node: licenses"
  $results += TryRun "node:licenses" {
    npx --yes license-checker --json > $Reports\node-licenses.json
  }

  # Test runner auto-detect
  $runner = $null
  if ($pkg -and $pkg.devDependencies -and ($pkg.devDependencies.PSObject.Properties.Name -contains "vitest")) { $runner = "vitest" }
  elseif ($pkg -and $pkg.devDependencies -and ($pkg.devDependencies.PSObject.Properties.Name -contains "jest")) { $runner = "jest" }

  if ($runner -eq "vitest") {
    Step "Node: vitest (smoke)"
    $results += TryRun "node:vitest" {
      npx --yes vitest run --reporter=dot | Out-File -Encoding utf8 $Reports\vitest.txt
    }
  } elseif ($runner -eq "jest") {
    Step "Node: jest (smoke)"
    $results += TryRun "node:jest" {
      npx --yes jest --ci --reporters=default | Out-File -Encoding utf8 $Reports\jest.txt
    }
  } else {
    $results += @{ name="node:tests"; status="skipped"; reason="no vitest/jest detected" }
  }

  Step "Node: Semgrep (auto config)"
  $results += TryRun "node:semgrep" {
    python -m semgrep --config auto --json --error --timeout 120 > $Reports\semgrep-node.json
  }

  Step "Node: secrets scan"
  $results += TryRun "node:detect-secrets" {
    python -m detect_secrets scan --all-files > $Reports\detect-secrets-node.json
  }
} else {
  $results += @{ name="node"; status="skipped"; reason="no package.json" }
}

# ------------------ Consolidated summary ------------------
$summary = @{
  repo = (Split-Path -Leaf $Root)
  generated_at = (Get-Date).ToString("o")
  stacks = @{ python = [bool]$isPy; node = [bool]$isNode }
  outputs = @{
    git              = "reports/git.json"
    ruff             = "reports/ruff.json"
    mypy             = "reports/mypy.txt"
    bandit           = "reports/bandit.json"
    pip_audit        = "reports/pip-audit.json"
    py_licenses      = "reports/py-licenses.json"
    pytest           = "reports/pytest.txt"
    semgrep_py       = "reports/semgrep.json"
    detect_secrets   = "reports/detect-secrets.json"
    eslint           = "reports/eslint.json"
    tsc              = "reports/tsc.txt"
    npm_audit        = "reports/npm-audit.json"
    depcheck         = "reports/depcheck.txt"
    node_licenses    = "reports/node-licenses.json"
    vitest           = "reports/vitest.txt"
    jest             = "reports/jest.txt"
    semgrep_node     = "reports/semgrep-node.json"
    detect_secrets_n = "reports/detect-secrets-node.json"
  }
  steps = $results
}
$summary | ConvertTo-Json -Depth 6 | Out-File -Encoding utf8 (Join-Path $Reports "_summary.json")

Write-Host ""
Write-Host "✅ Done. Reports in: $Reports"
Write-Host "Share reports/_summary.json (and any noisy files it points to) and I’ll triage with fix-ready patches."
