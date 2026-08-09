$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $project "backend"
$venvPython = Join-Path $project ".venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { (Get-Command python -ErrorAction Stop).Source }

$commands = @(
  @{ Name = "Accounts MCP"; Args = "-m uvicorn services.accounts:app --port 8101" },
  @{ Name = "Transactions MCP"; Args = "-m uvicorn services.transactions:app --port 8102" },
  @{ Name = "Service MCP"; Args = "-m uvicorn services.service:app --port 8103" },
  @{ Name = "Coordinator API"; Args = "-m uvicorn app.main:app --port 8000" }
)

foreach ($item in $commands) {
  Start-Process $python -ArgumentList $item.Args -WorkingDirectory $backend -WindowStyle Hidden
  Write-Host "Started $($item.Name)"
}

Set-Location $project
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000"
npm.cmd run dev
