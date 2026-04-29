# Entry point for beginners on Windows.
$ErrorActionPreference = "Stop"
Write-Host "CORA" -ForegroundColor Cyan
Write-Host "Codex Literature Review Automation" -ForegroundColor DarkCyan
Write-Host "Project root: $PSScriptRoot"

function Test-Cmd($name) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { Write-Host "[OK] $name -> $($cmd.Source)" -ForegroundColor Green; return $true }
    Write-Host "[WARN] $name not found" -ForegroundColor Yellow
    return $false
}

$hasPy = Test-Cmd py
if (-not $hasPy) { Test-Cmd python | Out-Null }

Write-Host "`nRunning environment check..." -ForegroundColor Cyan
if ($hasPy) {
    py "$PSScriptRoot\scripts\reviewflow.py" check
} else {
    python "$PSScriptRoot\scripts\reviewflow.py" check
}

Write-Host "`nNext step:" -ForegroundColor Cyan
Write-Host 'py scripts\reviewflow.py intake --name my_first_review --topic "your review topic" --output .\outputs'
Write-Host 'py scripts\reviewflow.py run --project .\outputs\my_first_review'
