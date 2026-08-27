@echo off
REM ============================================================================
REM 121XML Website Deployment Script for Windows
REM Deploy to HostArmada cPanel - hosting121.com
REM ============================================================================

setlocal enabledelayedexpansion

REM Configuration - EDIT THESE
set CPANEL_USER=121xml
set SERVER=hosting121.com
set DOMAIN=121xml.com
set SSH_PORT=22
set SOURCE_FILE=website_index.html
set REMOTE_PATH=public_html

cls
echo.
echo ============================================================================
echo                121XML Website Deployment to HostArmada
echo ============================================================================
echo.

REM Step 1: Verify file exists
echo [Step 1/4] Verifying source file...
if not exist "%SOURCE_FILE%" (
    echo ERROR: %SOURCE_FILE% not found in current directory
    echo.
    echo Make sure website_index.html is in: %cd%
    pause
    exit /b 1
)
echo [OK] Source file found: %SOURCE_FILE%
for %%A in ("%SOURCE_FILE%") do set FILE_SIZE=%%~zA
echo      File size: %FILE_SIZE% bytes
echo.

REM Step 2: Check for SSH/SCP tools
echo [Step 2/4] Checking for SSH tools...
where scp >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: SCP not found in PATH
    echo.
    echo You need Git Bash or PuTTY installed with SSH tools
    echo.
    echo Option 1 (Recommended): Install Git Bash
    echo   https://git-scm.com/download/win
    echo.
    echo Option 2: Use WinSCP GUI instead
    echo   https://winscp.net/eng/docs/guide_windows_openssh_key
    echo.
    pause
    exit /b 1
)
echo [OK] SSH tools available
echo.

REM Step 3: Upload file
echo [Step 3/4] Uploading website file to %SERVER%...
echo.
scp -P %SSH_PORT% "%SOURCE_FILE%" "%CPANEL_USER%@%SERVER%:%REMOTE_PATH%/website_index.html"
if %errorlevel% neq 0 (
    echo ERROR: Upload failed
    echo.
    echo Check your credentials:
    echo   Username: %CPANEL_USER%
    echo   Server: %SERVER%
    echo   Port: %SSH_PORT%
    echo.
    pause
    exit /b 1
)
echo [OK] File uploaded successfully
echo.

REM Step 4: Rename and finalize
echo [Step 4/4] Finalizing deployment...
ssh -p %SSH_PORT% "%CPANEL_USER%@%SERVER%" "cd ~/%REMOTE_PATH% && mv website_index.html index.html && chmod 644 index.html && ls -lh index.html"
if %errorlevel% neq 0 (
    echo ERROR: Finalization failed
    pause
    exit /b 1
)
echo [OK] Deployment finalized
echo.

REM Success message
echo ============================================================================
echo                    ✓ DEPLOYMENT SUCCESSFUL
echo ============================================================================
echo.
echo Your website is now live!
echo.
echo Website URL:
echo   https://%DOMAIN%
echo   http://%DOMAIN%
echo.
echo Next steps:
echo   1. Open browser and visit https://%DOMAIN%
echo   2. Test the interactive features
echo   3. Check mobile responsiveness
echo   4. Set up Google Analytics (optional)
echo.
echo If HTTPS shows certificate error:
echo   - This is normal during SSL setup
echo   - AutoSSL usually activates within 30 minutes
echo   - Refresh page after 30 minutes
echo.
echo For backend deployment (Python API):
echo   See DEPLOYMENT_AND_GETTING_STARTED.md
echo.
echo ============================================================================
echo.
pause
