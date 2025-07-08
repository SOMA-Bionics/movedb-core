# PowerShell script equivalent to Makefile commands for MoveDB Core
param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [string]$File,
    [string]$Pattern,
    [string]$Version
)

function Show-Help {
    Write-Host "MoveDB Core Development Commands (PowerShell):" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\scripts\make.ps1 <target>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Environment Setup:" -ForegroundColor Green
    Write-Host "  install          Install package in development mode"
    Write-Host "  install-dev      Install package with development dependencies"
    Write-Host "  check-dev-deps   Check if development dependencies are installed"
    Write-Host "  dev-setup        Full development setup with dependency check"
    Write-Host ""
    Write-Host "Testing:" -ForegroundColor Green
    Write-Host "  test             Run all tests with coverage"
    Write-Host "  test-quick       Run tests without coverage (faster)"
    Write-Host "  test-specific    Run specific test file (use -File parameter)"
    Write-Host "  test-pattern     Run tests matching pattern (use -Pattern parameter)"
    Write-Host ""
    Write-Host "Code Quality:" -ForegroundColor Green
    Write-Host "  lint             Run all linting checks"
    Write-Host "  lint-fix         Auto-fix linting issues"
    Write-Host "  lint-code        Run code linting only (no docs)"
    Write-Host "  lint-fix-code    Auto-fix code linting issues only (no docs)"
    Write-Host "  format           Format code with black"
    Write-Host ""
    Write-Host "Build and Package:" -ForegroundColor Green
    Write-Host "  build            Build conda package"
    Write-Host "  build-wheel      Build Python wheel"
    Write-Host "  clean            Clean build artifacts"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\scripts\make.ps1 install-dev"
    Write-Host "  .\scripts\make.ps1 lint-fix-code"
    Write-Host "  .\scripts\make.ps1 test-specific -File test_basic.py"
    Write-Host "  .\scripts\make.ps1 test-pattern -Pattern trial"
}

function Install-Package {
    Write-Host "Installing package in development mode..." -ForegroundColor Yellow
    pip install -e .
}

function Install-Dev {
    Write-Host "Installing package with development dependencies..." -ForegroundColor Yellow
    pip install -e ".[dev]"
}

function Check-DevDeps {
    Write-Host "Checking development dependencies..." -ForegroundColor Yellow
    try {
        python -c "import black, flake8, mypy, isort" 2>$null
        Write-Host "✅ Development dependencies are installed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Development dependencies missing. Run: .\scripts\make.ps1 install-dev" -ForegroundColor Red
        exit 1
    }
}

function Dev-Setup {
    Install-Dev
    Check-DevDeps
}

function Run-Tests {
    Write-Host "Running all tests with coverage..." -ForegroundColor Yellow
    python scripts/run_tests.py
}

function Run-TestsQuick {
    Write-Host "Running tests without coverage..." -ForegroundColor Yellow
    pytest --no-cov
}

function Run-TestsSpecific {
    if (-not $File) {
        Write-Host "❌ Please specify a file with -File parameter" -ForegroundColor Red
        exit 1
    }
    Write-Host "Running specific test file: $File" -ForegroundColor Yellow
    python scripts/run_tests.py --file $File
}

function Run-TestsPattern {
    if (-not $Pattern) {
        Write-Host "❌ Please specify a pattern with -Pattern parameter" -ForegroundColor Red
        exit 1
    }
    Write-Host "Running tests matching pattern: $Pattern" -ForegroundColor Yellow
    python scripts/run_tests.py --pattern $Pattern
}

function Run-Lint {
    Write-Host "Running all linting checks..." -ForegroundColor Yellow
    Write-Host "Running flake8..."
    flake8 src/ tests/
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ flake8 failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "Running mypy..."
    mypy src/movedb/ --ignore-missing-imports
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  mypy warnings found (non-blocking)" -ForegroundColor Yellow
    }
    Write-Host "Checking black formatting..."
    black --check --diff src/ tests/
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ black formatting issues found" -ForegroundColor Red
        exit 1
    }
    Write-Host "Checking import sorting..."
    isort --check-only --diff src/ tests/
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ isort import sorting issues found" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ All linting checks passed!" -ForegroundColor Green
}

function Fix-Lint {
    Write-Host "Auto-fixing linting issues..." -ForegroundColor Yellow
    Write-Host "Formatting code with black..."
    black src/ tests/
    Write-Host "Sorting imports with isort..."
    isort src/ tests/
    Write-Host "✅ Code formatted and imports sorted!" -ForegroundColor Green
}

function Run-LintCode {
    Write-Host "Running code linting only..." -ForegroundColor Yellow
    Write-Host "Running flake8..."
    flake8 src/ tests/
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ flake8 failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "Running mypy..."
    mypy src/movedb/ --ignore-missing-imports
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  mypy warnings found (non-blocking)" -ForegroundColor Yellow
    }
    Write-Host "Checking black formatting..."
    black --check --diff src/ tests/
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ black formatting issues found" -ForegroundColor Red
        exit 1
    }
    Write-Host "Checking import sorting..."
    isort --check-only --diff src/ tests/
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ isort import sorting issues found" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ All code linting checks passed!" -ForegroundColor Green
}

function Fix-LintCode {
    Write-Host "Auto-fixing code linting issues only..." -ForegroundColor Yellow
    Write-Host "Formatting code with black..."
    black src/ tests/
    Write-Host "Sorting imports with isort..."
    isort src/ tests/
    Write-Host "✅ Code formatted and imports sorted!" -ForegroundColor Green
}

function Format-Code {
    Write-Host "Formatting code with black..." -ForegroundColor Yellow
    black src/ tests/
}

function Build-Package {
    Write-Host "Building conda package..." -ForegroundColor Yellow
    & .\scripts\build_conda.ps1
}

function Build-Wheel {
    Write-Host "Building Python wheel..." -ForegroundColor Yellow
    python -m build
}

function Clean-Artifacts {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    Get-ChildItem -Path . -Filter "*.egg-info" -Recurse | Remove-Item -Recurse -Force
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
    if (Test-Path ".mypy_cache") { Remove-Item -Recurse -Force ".mypy_cache" }
    Get-ChildItem -Path . -Name "__pycache__" -Recurse | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Filter "*.pyc" -Recurse | Remove-Item -Force
    Write-Host "✅ Build artifacts cleaned!" -ForegroundColor Green
}

# Main command switch
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Package }
    "install-dev" { Install-Dev }
    "check-dev-deps" { Check-DevDeps }
    "dev-setup" { Dev-Setup }
    "test" { Run-Tests }
    "test-quick" { Run-TestsQuick }
    "test-specific" { Run-TestsSpecific }
    "test-pattern" { Run-TestsPattern }
    "lint" { Run-Lint }
    "lint-fix" { Fix-Lint }
    "lint-code" { Run-LintCode }
    "lint-fix-code" { Fix-LintCode }
    "format" { Format-Code }
    "build" { Build-Package }
    "build-wheel" { Build-Wheel }
    "clean" { Clean-Artifacts }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\scripts\make.ps1 help' for available commands" -ForegroundColor Yellow
        exit 1
    }
}
