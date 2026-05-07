$ErrorActionPreference = "Stop"

Write-Host "Enabling Windows features required for Podman Desktop..." -ForegroundColor Cyan
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -All -NoRestart
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -All -NoRestart

Write-Host "Updating WSL..." -ForegroundColor Cyan
wsl --update

Write-Host "Installing WSL without a default Linux distribution..." -ForegroundColor Cyan
wsl --install --no-distribution

Write-Host ""
Write-Host "Setup step completed." -ForegroundColor Green
Write-Host "Restart Windows now, then open Podman Desktop and finish the onboarding wizard." -ForegroundColor Yellow
