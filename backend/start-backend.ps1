# PDF Generator - Backend Startup Script
# This script sets environment variables and starts the backend server

# Set environment variables
# Set environment variables (optional, .env is preferred)
# $env:CORS_ORIGINS="http://localhost:3000,http://localhost:3001"

Write-Host "Starting PDF Generator Backend..." -ForegroundColor Green
Write-Host "Environment variables set:" -ForegroundColor Yellow
Write-Host "  CORS_ORIGINS: $env:CORS_ORIGINS"
Write-Host ""
Write-Host ""

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start the server
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
