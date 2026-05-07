$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Checking Podman..." -ForegroundColor Cyan
podman version

Write-Host "Checking Podman machine..." -ForegroundColor Cyan
podman machine list

Write-Host "Starting compose stack..." -ForegroundColor Cyan
podman compose up --build
