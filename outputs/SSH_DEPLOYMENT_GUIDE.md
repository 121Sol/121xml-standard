# 121XML SSH Deployment Guide (PowerShell)

## Prerequisites

### Windows: Install OpenSSH
PowerShell 7.1+ or Windows 10 v1803+ includes OpenSSH by default.

**Verify SSH is installed:**
```powershell
ssh -V
```

**If not installed:**
- Download: https://github.com/PowerShell/Win32-OpenSSH/releases
- Or: Install Git for Windows (includes SSH)

### For Password Authentication
Install `sshpass` (if using deploy_ssh.ps1):
```powershell
# Option 1: Using Chocolatey
choco install sshpass

# Option 2: Download from GitHub
# https://github.com/kevinburke/sshpass/releases
```

---

## Quick Deploy (30 seconds)

### Method 1: Password Authentication (Simplest)

**Download and run the script:**
```powershell
# 1. Open PowerShell in the directory with index.html
cd C:\path\to\121xml\files

# 2. Run the deployment script
.\deploy_ssh.ps1

# 3. When prompted, enter your SSH password
```

**Server details:**
- Host: 121xml.com
- Port: 19199
- Username: xml
- Password: [your SSH password]

---

### Method 2: SSH Key Authentication (More Secure)

**If you already have SSH keys:**
```powershell
# 1. Open PowerShell where index.html is located
cd C:\path\to\121xml\files

# 2. Run the key-based deployment
.\deploy_ssh_key.ps1 -SSHKeyPath "$HOME\.ssh\id_rsa"

# 3. No password prompt needed!
```

**Generate SSH key (first time only):**
```powershell
ssh-keygen -t rsa -b 4096 -f "$HOME\.ssh\id_rsa"
# Press Enter for all prompts (no passphrase)

# Then copy public key to server:
cat $HOME\.ssh\id_rsa.pub | ssh -p 19199 xml@121xml.com "cat >> ~/.ssh/authorized_keys"
```

---

## Step-by-Step Setup

### 1. Prepare Files
```powershell
# Navigate to where you have index.html
cd C:\Users\YourUser\Documents\121xml

# Verify file exists
ls index.html
```

### 2. Choose Method

**Password Auth (simpler):**
```powershell
.\deploy_ssh.ps1
# Then enter password when prompted
```

**SSH Key (recommended for automation):**
```powershell
.\deploy_ssh_key.ps1
```

### 3. Verify Deployment

After deployment completes:
```powershell
# Open your browser
Start-Process "https://121xml.com"

# Or manually verify via SSH:
ssh -p 19199 xml@121xml.com "ls -la /var/www/121xml/index.html"
```

---

## Troubleshooting

### "SSH command not found"
**Solution:** Install OpenSSH or Git for Windows
```powershell
# Option 1: Git for Windows
# Download: https://git-scm.com/download/win

# Option 2: Windows Terminal (has OpenSSH built-in)
# Install from Microsoft Store
```

### "Permission denied"
**Solution:** Check credentials
```powershell
# Test connection manually:
ssh -p 19199 xml@121xml.com

# Verify password:
ssh -p 19199 -o PubkeyAuthentication=no xml@121xml.com "whoami"
```

### "Could not resolve hostname"
**Solution:** Check host name
```powershell
# Verify DNS:
nslookup 121xml.com

# Test connection:
Test-NetConnection -ComputerName 121xml.com -Port 19199
```

### Script won't run
**Solution:** Enable script execution
```powershell
# Allow scripts in current process only:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Then run script:
.\deploy_ssh.ps1
```

---

## Post-Deployment

### Verify Website is Live
1. Visit https://121xml.com
2. Check all sections load
3. Test interactive features
4. Clear cache if needed (Ctrl+Shift+Delete)

### Check File on Server
```powershell
ssh -p 19199 xml@121xml.com "ls -la /var/www/121xml/index.html"
```

---

## Security Notes

✅ **Password Script (deploy_ssh.ps1):**
- Password is prompted interactively
- Never stored in script
- Cleared from memory after use

✅ **SSH Key Script (deploy_ssh_key.ps1) - RECOMMENDED:**
- No password in script
- SSH key authentication
- More secure for automation

⚠️ **Never:**
- Hardcode credentials in scripts
- Share SSH passwords
- Store passwords in version control

---

## Ready to Deploy

**Your deployment package includes:**
- ✅ index.html (55KB - ready to deploy)
- ✅ deploy_ssh.ps1 (password-based deployment)
- ✅ deploy_ssh_key.ps1 (key-based deployment)
- ✅ SSH_DEPLOYMENT_GUIDE.md (this guide)

**Next step:** Run deploy_ssh.ps1 or deploy_ssh_key.ps1 with your SSH password/key

---
*© 2026 121 Solutions USA. All rights reserved. The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive property of 121 Solutions USA. Unauthorized use, reproduction, or distribution of this material is strictly prohibited without prior written permission.*