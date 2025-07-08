@echo off
REM Windows batch script equivalent to Makefile commands for MoveDB Core

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="install" goto :install
if "%1"=="install-dev" goto :install-dev
if "%1"=="test" goto :test
if "%1"=="test-quick" goto :test-quick
if "%1"=="lint" goto :lint
if "%1"=="lint-fix" goto :lint-fix
if "%1"=="lint-code" goto :lint-code
if "%1"=="lint-fix-code" goto :lint-fix-code
if "%1"=="format" goto :format
if "%1"=="build" goto :build
if "%1"=="build-wheel" goto :build-wheel
if "%1"=="clean" goto :clean
if "%1"=="dev-setup" goto :dev-setup
if "%1"=="check-dev-deps" goto :check-dev-deps

echo Unknown command: %1
echo Run "scripts\make.bat help" for available commands
exit /b 1

:help
echo MoveDB Core Development Commands (Windows):
echo ==========================================
echo.
echo Usage: scripts\make.bat ^<target^>
echo.
echo Environment Setup:
echo   install          Install package in development mode
echo   install-dev      Install package with development dependencies
echo   check-dev-deps   Check if development dependencies are installed
echo   dev-setup        Full development setup with dependency check
echo.
echo Testing:
echo   test             Run all tests with coverage
echo   test-quick       Run tests without coverage (faster)
echo.
echo Code Quality:
echo   lint             Run all linting checks
echo   lint-fix         Auto-fix linting issues
echo   lint-code        Run code linting only (no docs)
echo   lint-fix-code    Auto-fix code linting issues only (no docs)
echo   format           Format code with black
echo.
echo Build and Package:
echo   build            Build conda package
echo   build-wheel      Build Python wheel
echo   clean            Clean build artifacts
echo.
echo Examples:
echo   scripts\make.bat install-dev
echo   scripts\make.bat lint-fix-code
echo   scripts\make.bat test-quick
goto :eof

:install
echo Installing package in development mode...
pip install -e .
goto :eof

:install-dev
echo Installing package with development dependencies...
pip install -e ".[dev]"
goto :eof

:check-dev-deps
echo Checking development dependencies...
python -c "import black, flake8, mypy, isort" 2>nul && (
    echo ✅ Development dependencies are installed
) || (
    echo ❌ Development dependencies missing. Run: scripts\make.bat install-dev
    exit /b 1
)
goto :eof

:dev-setup
call :install-dev
call :check-dev-deps
goto :eof

:test
echo Running all tests with coverage...
python scripts/run_tests.py
goto :eof

:test-quick
echo Running tests without coverage...
pytest --no-cov
goto :eof

:lint
echo Running all linting checks...
echo Running flake8...
flake8 src/ tests/ || (echo ❌ flake8 failed & exit /b 1)
echo Running mypy...
mypy src/movedb/ --ignore-missing-imports || echo ⚠️  mypy warnings found (non-blocking)
echo Checking black formatting...
black --check --diff src/ tests/ || (echo ❌ black formatting issues found & exit /b 1)
echo Checking import sorting...
isort --check-only --diff src/ tests/ || (echo ❌ isort import sorting issues found & exit /b 1)
echo ✅ All linting checks passed!
goto :eof

:lint-fix
echo Auto-fixing linting issues...
echo Formatting code with black...
black src/ tests/
echo Sorting imports with isort...
isort src/ tests/
echo ✅ Code formatted and imports sorted!
goto :eof

:lint-code
echo Running code linting only...
echo Running flake8...
flake8 src/ tests/ || (echo ❌ flake8 failed & exit /b 1)
echo Running mypy...
mypy src/movedb/ --ignore-missing-imports || echo ⚠️  mypy warnings found (non-blocking)
echo Checking black formatting...
black --check --diff src/ tests/ || (echo ❌ black formatting issues found & exit /b 1)
echo Checking import sorting...
isort --check-only --diff src/ tests/ || (echo ❌ isort import sorting issues found & exit /b 1)
echo ✅ All code linting checks passed!
goto :eof

:lint-fix-code
echo Auto-fixing code linting issues only...
echo Formatting code with black...
black src/ tests/
echo Sorting imports with isort...
isort src/ tests/
echo ✅ Code formatted and imports sorted!
goto :eof

:format
echo Formatting code with black...
black src/ tests/
goto :eof

:build
echo Building conda package...
call scripts\build_conda.bat
goto :eof

:build-wheel
echo Building Python wheel...
python -m build
goto :eof

:clean
echo Cleaning build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info
if exist htmlcov rmdir /s /q htmlcov
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist .mypy_cache rmdir /s /q .mypy_cache
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc 2>nul
echo ✅ Build artifacts cleaned!
goto :eof
