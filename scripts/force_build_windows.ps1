# Force Build Script for Windows
# Handles OneDrive and file locking issues

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Bulletin Builder - Force Build (Windows)" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Step 1: Stop any running Bulletin Builder instances
Write-Host "Step 1: Stopping any running Bulletin Builder instances..." -ForegroundColor Yellow
Stop-Process -Name "bulletin" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -like "*Bulletin*"}
Start-Sleep -Seconds 2
Write-Host "  Done`n" -ForegroundColor Green

# Step 2: Temporarily pause OneDrive
Write-Host "Step 2: Attempting to pause OneDrive..." -ForegroundColor Yellow
try {
    $onedrive = Get-Process "OneDrive" -ErrorAction SilentlyContinue
    if ($onedrive) {
        Write-Host "  OneDrive is running. Attempting to pause sync..." -ForegroundColor Yellow
        # Try to pause OneDrive via command
        Start-Process "powershell" -ArgumentList "-Command `"& {`$null = (New-Object -ComObject Shell.Application).NameSpace(0x01).Items() | Where-Object {`$_.Name -eq 'OneDrive'} | ForEach-Object {`$_.InvokeVerb('pause')}}`"" -NoNewWindow -Wait -ErrorAction SilentlyContinue
        Write-Host "  Please manually pause OneDrive if automatic pause failed:" -ForegroundColor Yellow
        Write-Host "  1. Right-click OneDrive icon in system tray" -ForegroundColor Yellow
        Write-Host "  2. Click 'Pause syncing' -> '2 hours'" -ForegroundColor Yellow
        Write-Host "`n  Press Enter after pausing OneDrive (or skip if already paused)..." -ForegroundColor Cyan
        Read-Host
    } else {
        Write-Host "  OneDrive not running`n" -ForegroundColor Green
    }
} catch {
    Write-Host "  Could not pause OneDrive automatically. Please pause manually.`n" -ForegroundColor Yellow
}

# Step 3: Forcefully remove build and dist directories
Write-Host "Step 3: Removing old build artifacts..." -ForegroundColor Yellow

$attempts = 0
$maxAttempts = 3

while ($attempts -lt $maxAttempts) {
    $attempts++
    Write-Host "  Attempt $attempts of $maxAttempts..." -ForegroundColor Gray
    
    try {
        # Remove build directory
        if (Test-Path "build") {
            Remove-Item -Path "build" -Recurse -Force -ErrorAction Stop
            Write-Host "  Removed build/" -ForegroundColor Green
        }
        
        # Remove dist directory
        if (Test-Path "dist") {
            Remove-Item -Path "dist" -Recurse -Force -ErrorAction Stop
            Write-Host "  Removed dist/" -ForegroundColor Green
        }
        
        Write-Host "  Cleanup successful!`n" -ForegroundColor Green
        break
        
    } catch {
        if ($attempts -lt $maxAttempts) {
            Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "  Waiting 5 seconds before retry..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        } else {
            Write-Host "  WARNING: Could not remove all files. Continuing anyway...`n" -ForegroundColor Yellow
        }
    }
}

# Step 4: Run PyInstaller build
Write-Host "Step 4: Running PyInstaller build..." -ForegroundColor Yellow
Write-Host "  This will take several minutes...`n" -ForegroundColor Gray

python scripts/build_exe.py --no-clean

$buildExitCode = $LASTEXITCODE

# Step 5: Check if build succeeded
Write-Host "`nStep 5: Checking build results..." -ForegroundColor Yellow

$exeInBuild = Test-Path "build\bulletin_builder\bulletin.exe"
$exeInDist = Test-Path "dist\bulletin\bulletin.exe"
$distHasInternal = Test-Path "dist\bulletin\_internal"

Write-Host "  EXE in build/: $exeInBuild" -ForegroundColor $(if ($exeInBuild) {"Green"} else {"Red"})
Write-Host "  EXE in dist/: $exeInDist" -ForegroundColor $(if ($exeInDist) {"Green"} else {"Yellow"})
Write-Host "  dist has _internal/: $distHasInternal`n" -ForegroundColor $(if ($distHasInternal) {"Green"} else {"Yellow"})

# Step 6: Handle partial build (if dist incomplete but build succeeded)
if ($exeInBuild -and -not $distHasInternal) {
    Write-Host "Step 6: Build succeeded but COLLECT failed. Attempting manual copy..." -ForegroundColor Yellow
    
    try {
        # Wait a bit more for file locks to release
        Write-Host "  Waiting 10 seconds for file locks to release..." -ForegroundColor Gray
        Start-Sleep -Seconds 10
        
        # Create dist directory if needed
        if (-not (Test-Path "dist")) {
            New-Item -Path "dist" -ItemType Directory -Force | Out-Null
        }
        
        # Remove any partial dist/bulletin
        if (Test-Path "dist\bulletin") {
            Remove-Item -Path "dist\bulletin" -Recurse -Force -ErrorAction Stop
        }
        
        # Copy from build to dist
        Write-Host "  Copying from build\bulletin_builder\ to dist\bulletin\..." -ForegroundColor Gray
        
        # Use robocopy for better handling of locked files
        $robocopyArgs = @(
            "build\bulletin_builder",
            "dist\bulletin",
            "/E",           # Copy subdirectories including empty
            "/MT:8",        # Multi-threaded (8 threads)
            "/R:2",         # Retry 2 times
            "/W:5",         # Wait 5 seconds between retries
            "/NFL",         # No file list
            "/NDL",         # No directory list
            "/NP"           # No progress
        )
        
        $robocopyResult = robocopy @robocopyArgs
        
        # Robocopy exit codes: 0-7 are success, 8+ are errors
        if ($LASTEXITCODE -lt 8) {
            Write-Host "  Manual copy successful!`n" -ForegroundColor Green
        } else {
            Write-Host "  Manual copy had issues (exit code: $LASTEXITCODE)`n" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "  Manual copy failed: $($_.Exception.Message)`n" -ForegroundColor Red
    }
}

# Step 7: Run validation
Write-Host "Step 7: Validating build..." -ForegroundColor Yellow
python scripts/validate_build.py

$validationExitCode = $LASTEXITCODE

# Step 8: Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Build Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if ($validationExitCode -eq 0) {
    Write-Host "SUCCESS: Build is complete and validated!" -ForegroundColor Green
    Write-Host "`nExecutable location: dist\bulletin\bulletin.exe" -ForegroundColor Green
    Write-Host "`nTo test:" -ForegroundColor Cyan
    Write-Host "  cd dist\bulletin" -ForegroundColor Gray
    Write-Host "  .\bulletin.exe --gui" -ForegroundColor Gray
} elseif ($exeInBuild) {
    Write-Host "PARTIAL: Build succeeded but distribution may be incomplete" -ForegroundColor Yellow
    Write-Host "`nYou can use the EXE from the build directory:" -ForegroundColor Yellow
    Write-Host "  build\bulletin_builder\bulletin.exe --gui" -ForegroundColor Gray
    Write-Host "`nOr try the dist version (may have issues):" -ForegroundColor Yellow
    Write-Host "  dist\bulletin\bulletin.exe --gui" -ForegroundColor Gray
} else {
    Write-Host "FAILED: Build did not complete successfully" -ForegroundColor Red
    Write-Host "`nCheck the error messages above for details." -ForegroundColor Red
}

Write-Host "`n============================================================`n" -ForegroundColor Cyan

# Step 9: Resume OneDrive reminder
Write-Host "REMINDER: Don't forget to resume OneDrive syncing!" -ForegroundColor Yellow
Write-Host "Right-click OneDrive icon -> Resume syncing`n" -ForegroundColor Yellow

exit $validationExitCode
