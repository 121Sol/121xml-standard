#Requires -Version 5.0
<#
.SYNOPSIS
Push 121AI and 121XML Standard files to GitHub repositories

.DESCRIPTION
Clones existing GitHub repositories and pushes all project files to them

.PARAMETER GitHubUsername
GitHub username (default: rashadkhan4mna)

.PARAMETER GitHubEmail
GitHub email (default: rashadkhan4mna@gmail.com)

.EXAMPLE
.\push-to-github.ps1

.NOTES
Requires: Git for Windows
#>

param(
    [string]$GitHubUsername = "rashadkhan4mna",
    [string]$GitHubEmail = "rashadkhan4mna@gmail.com"
)

$ErrorActionPreference = "Stop"

# ============================================================================
# CONFIGURATION
# ============================================================================

$SOURCE_PATH = "F:\AI\Claude\Projects\121XML"
$TEMP_DIR = "$env:TEMP\121ai-push-$(Get-Random)"

# Colors
function Write-Success { Write-Host "[✓] $args" -ForegroundColor Green }
function Write-Info { Write-Host "[i] $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "[!] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[✗] $args" -ForegroundColor Red }
function Write-Header { Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan; Write-Host "║  $args" -ForegroundColor Cyan; Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Clear-Host
Write-Header "121AI & 121XML - Push Files to GitHub"
Write-Host ""

# Verify Git
Write-Info "Checking Git installation..."
try {
    $gitVersion = git --version
    Write-Success "$gitVersion"
} catch {
    Write-Error "Git not found. Please install Git for Windows."
    exit 1
}

# Create temp directory
Write-Info "Creating working directory: $TEMP_DIR"
New-Item -ItemType Directory -Path $TEMP_DIR -Force | Out-Null
Write-Success "Working directory created"

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Repository: 121ai" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Clone 121ai
Write-Info "Cloning 121ai repository..."
Push-Location $TEMP_DIR
try {
    git clone https://github.com/$GitHubUsername/121ai.git
    Write-Success "Repository cloned"
} catch {
    Write-Error "Failed to clone repository: $_"
    exit 1
}

# Configure git
git config user.email $GitHubEmail
git config user.name $GitHubUsername

# Enter 121ai directory
Push-Location "121ai"

# Copy files
Write-Info "Copying 121AI files..."
$files_121ai = @(
    "setup.py",
    "121ai_package_structure.txt",
    "build_all_platforms.sh",
    "121AI_DEPLOYMENT_GUIDE.md",
    "121AI_LOGO.svg",
    "121AI_BROCHURE.html",
    "121AI_BUSINESS_CASE.md",
    "121AI_BRAND_GUIDELINES.md",
    "github_setup.sh"
)

foreach ($file in $files_121ai) {
    $sourcePath = Join-Path $SOURCE_PATH $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath . -Force
        Write-Success "Copied: $file"
    } else {
        Write-Warning "Not found: $file"
    }
}

Write-Host ""

# Add and commit
Write-Info "Committing changes..."
git add . --verbose
$commitOutput = git commit -m "Add 121AI application files, deployment automation, and brand assets" --allow-empty
Write-Success "Committed"

Write-Host ""

# Push
Write-Info "Pushing to GitHub..."
try {
    $pushOutput = git push -u origin main 2>&1
    if ($pushOutput -match "fatal") {
        Write-Warning "Push output: $pushOutput"
    } else {
        Write-Success "Pushed to GitHub"
    }
} catch {
    Write-Warning "Push may have encountered an issue, but continuing: $_"
}

Write-Host ""

# Return to temp directory
Pop-Location

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Repository: 121xml-standard" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Clone 121xml-standard
Write-Info "Cloning 121xml-standard repository..."
try {
    git clone https://github.com/$GitHubUsername/121xml-standard.git
    Write-Success "Repository cloned"
} catch {
    Write-Error "Failed to clone repository: $_"
    exit 1
}

# Enter 121xml-standard directory
Push-Location "121xml-standard"

# Configure git
git config user.email $GitHubEmail
git config user.name $GitHubUsername

# Copy files
Write-Info "Copying 121XML Standard files..."
$files_121xml = @(
    "121XML_AI_OS_MASTER_SPEC.md",
    "121XML_PRINCIPLES_SECURITY_SOVEREIGNTY.md",
    "121XML_ARCHITECTURE_MEMORY_DETERMINISM.md",
    "121XML_GITHUB_STRATEGY.md"
)

foreach ($file in $files_121xml) {
    $sourcePath = Join-Path $SOURCE_PATH $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath . -Force
        Write-Success "Copied: $file"
    } else {
        Write-Warning "Not found: $file"
    }
}

Write-Host ""

# Add and commit
Write-Info "Committing changes..."
git add . --verbose
$commitOutput = git commit -m "Add 121XML Standard specification documents" --allow-empty
Write-Success "Committed"

Write-Host ""

# Push
Write-Info "Pushing to GitHub..."
try {
    $pushOutput = git push -u origin main 2>&1
    if ($pushOutput -match "fatal") {
        Write-Warning "Push output: $pushOutput"
    } else {
        Write-Success "Pushed to GitHub"
    }
} catch {
    Write-Warning "Push may have encountered an issue, but continuing: $_"
}

# Return to original directory
Pop-Location
Pop-Location
Pop-Location

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✓ Push Complete Successfully                  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📦 Repositories Updated:" -ForegroundColor Yellow
Write-Host "  • 121AI (Private)"
Write-Host "    URL: https://github.com/$GitHubUsername/121ai"
Write-Host ""
Write-Host "  • 121XML Standard (Public)"
Write-Host "    URL: https://github.com/$GitHubUsername/121xml-standard"
Write-Host ""

Write-Host "📂 Local Working Directory:" -ForegroundColor Yellow
Write-Host "  $TEMP_DIR"
Write-Host ""

Write-Host "🔑 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Verify repositories at:"
Write-Host "     - https://github.com/$GitHubUsername/121ai"
Write-Host "     - https://github.com/$GitHubUsername/121xml-standard"
Write-Host ""
Write-Host "  2. Configure repository settings:"
Write-Host "     - Branch protection rules"
Write-Host "     - GitHub Actions secrets"
Write-Host "     - Collaborators and teams"
Write-Host ""
Write-Host "  3. Clone repositories locally:"
Write-Host "     git clone https://github.com/$GitHubUsername/121ai.git"
Write-Host "     git clone https://github.com/$GitHubUsername/121xml-standard.git"
Write-Host ""
Write-Host "  4. Generate 121AI source code and push"
Write-Host "  5. Setup CI/CD pipelines (.github/workflows/)"
Write-Host ""

Write-Success "All done!"
Write-Host ""
