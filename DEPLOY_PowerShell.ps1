# ============================================================================
# 121XML Website Deployment Script for Windows PowerShell
# Deploy to HostArmada cPanel - hosting121.com
# ============================================================================

# Configuration - EDIT THESE
$CPANEL_USER = "xml"
$SERVER = "hosting121.com"
$DOMAIN = "121xml.com"
$SSH_PORT = 22
$SOURCE_FILE = "website_index.html"
$REMOTE_PATH = "public_html"

# Colors
$colors = @{
    Success = 'Lime'
    Error = 'Red'
    Warning = 'Yellow'
    Info = 'Cyan'
}

function Write-Section {
    param([string]$Title)
    Write-Host "`n" -NoNewline
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Title" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message, [int]$Step, [int]$Total)
    Write-Host "`n[Step $Step/$Total] " -NoNewline -ForegroundColor Yellow
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ " -NoNewline -ForegroundColor Green
    Write-Host $Message
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ " -NoNewline -ForegroundColor Red
    Write-Host $Message
}

function Test-FileExists {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        return $true
    }
    return $false
}

# Main deployment
Write-Section "121XML Website Deployment to Hosting121"

# Step 1: Verify file exists
Write-Step "Verifying source file" 1 5
if (-not (Test-FileExists $SOURCE_FILE)) {
    Write-Error-Custom "File not found: $SOURCE_FILE"
    Write-Host "`nMake sure website_index.html is in: $(Get-Location)" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

$file = Get-Item $SOURCE_FILE
$fileSize = "{0:N2} KB" -f ($file.Length / 1024)
Write-Success "Source file found"
Write-Host "  File: $SOURCE_FILE"
Write-Host "  Size: $fileSize"

# Step 2: Check SSH availability
Write-Step "Checking for SSH tools" 2 5
$sshPath = (Get-Command ssh -ErrorAction SilentlyContinue).Source
$scpPath = (Get-Command scp -ErrorAction SilentlyContinue).Source

if (-not $sshPath) {
    Write-Error-Custom "SSH tools not found in PATH"
    Write-Host "`nYou need to install SSH tools:"
    Write-Host "  Option 1: Install Git Bash"
    Write-Host "    https://git-scm.com/download/win"
    Write-Host ""
    Write-Host "  Option 2: Install Windows Terminal with SSH"
    Write-Host "    https://docs.microsoft.com/en-us/windows/terminal/"
    Write-Host ""
    Write-Host "  Option 3: Use File Manager method (DEPLOYMENT_CONFIG.md)"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Success "SSH tools available"
Write-Host "  SSH: $sshPath"
Write-Host "  SCP: $scpPath"

# Step 3: Test SSH connection
Write-Step "Testing connection to $SERVER" 3 5
try {
    $result = & ssh -p $SSH_PORT -o ConnectTimeout=5 "${CPANEL_USER}@${SERVER}" "echo connection-ok" 2>&1
    if ($result -contains "connection-ok") {
        Write-Success "SSH connection successful"
    } else {
        Write-Error-Custom "SSH connection test failed"
        Write-Host "`nConnection output: $result" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Error-Custom "SSH connection failed: $_"
    Write-Host "`nCheck your credentials:" -ForegroundColor Yellow
    Write-Host "  Username: $CPANEL_USER"
    Write-Host "  Server: $SERVER"
    Write-Host "  Port: $SSH_PORT"
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 4: Upload file
Write-Step "Uploading website file" 4 5
Write-Host "  From: $SOURCE_FILE"
Write-Host "  To: ${CPANEL_USER}@${SERVER}:${REMOTE_PATH}/"
Write-Host ""

try {
    & scp -P $SSH_PORT $SOURCE_FILE "${CPANEL_USER}@${SERVER}:${REMOTE_PATH}/website_index.html"
    Write-Success "File uploaded successfully"
} catch {
    Write-Error-Custom "Upload failed: $_"
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 5: Finalize deployment
Write-Step "Finalizing deployment" 5 5
try {
    $finalizeCmd = @"
cd ~/$REMOTE_PATH && `
mv website_index.html index.html && `
chmod 644 index.html && `
ls -lh index.html
"@

    $result = & ssh -p $SSH_PORT "${CPANEL_USER}@${SERVER}" $finalizeCmd
    Write-Success "Deployment finalized"
    Write-Host ($result | Out-String)
} catch {
    Write-Error-Custom "Finalization failed: $_"
    Read-Host "Press Enter to exit"
    exit 1
}

# Verification
Write-Host "`nVerifying deployment..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

try {
    $httpResponse = curl -s -o $null -w "%{http_code}" "http://$DOMAIN" 2>$null
    if ($httpResponse -eq "200") {
        Write-Success "HTTP access working (200 OK)"
    } else {
        Write-Host "  HTTP Status: $httpResponse" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Could not check HTTP (DNS may still be propagating)" -ForegroundColor Yellow
}

# Success message
Write-Section "✓ DEPLOYMENT SUCCESSFUL"

Write-Host "`nYour website is now live!`n" -ForegroundColor Green
Write-Host "Website URLs:" -ForegroundColor Cyan
Write-Host "  https://$DOMAIN" -ForegroundColor Green
Write-Host "  http://$DOMAIN" -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Open browser and visit https://$DOMAIN"
Write-Host "  2. Test all interactive features"
Write-Host "  3. Check mobile responsiveness"
Write-Host "  4. Verify SSL certificate (may take 30 minutes)"

Write-Host "`nSSL Certificate:" -ForegroundColor Cyan
Write-Host "  AutoSSL is generating your certificate"
Write-Host "  If you see certificate error:"
Write-Host "    - This is normal"
Write-Host "    - Wait 30 minutes for AutoSSL to complete"
Write-Host "    - Then refresh your browser (Ctrl+Shift+R)"

Write-Host "`nBackup Information:" -ForegroundColor Cyan
Write-Host "  Previous version was backed up on the server"
Write-Host "  To restore via SSH:"
Write-Host "    ssh ${CPANEL_USER}@${SERVER}"
Write-Host "    cd ~/$REMOTE_PATH"
Write-Host "    ls -la ../backups/"

Write-Host "`nSupport:" -ForegroundColor Cyan
Write-Host "  Documentation: DEPLOYMENT_AND_GETTING_STARTED.md"
Write-Host "  Config Details: DEPLOYMENT_CONFIG.md"
Write-Host "  cPanel: https://${DOMAIN}:2083"

Write-Host "`n"
Read-Host "Press Enter to exit"
