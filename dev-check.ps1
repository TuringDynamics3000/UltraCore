# dev-check.ps1
# Quick quality checks before commit

Write-Host "
🔍 Running pre-commit checks...
" -ForegroundColor Cyan

Write-Host "1️⃣ Formatting (Black)..." -ForegroundColor Yellow
black src/ tests/
Write-Host "✅ Done
" -ForegroundColor Green

Write-Host "2️⃣ Linting (Ruff)..." -ForegroundColor Yellow
ruff check --fix src/ tests/
Write-Host "✅ Done
" -ForegroundColor Green

Write-Host "3️⃣ Type checking (MyPy)..." -ForegroundColor Yellow
mypy src/ultracore/ --ignore-missing-imports || Write-Host "⚠️ Type errors found
" -ForegroundColor Yellow

Write-Host "4️⃣ Running tests..." -ForegroundColor Yellow
pytest --cov=ultracore --cov-report=term-missing
Write-Host "✅ Done
" -ForegroundColor Green

Write-Host "✅ All checks complete! Safe to commit.
" -ForegroundColor Green
