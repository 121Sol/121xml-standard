# 121XML Deployment Configuration
## HostArmada/hosting121.com - cPanel Setup

---

## YOUR DEPLOYMENT INFO

```
┌─────────────────────────────────────────────────────────┐
│ DOMAIN:                  121xml.com                      │
│ HOSTING:                 HostArmada (hosting121.com)     │
│ CONTROL PANEL:           cPanel                          │
│ CPANEL USER:             121xml                          │
│ SERVER ADDRESS:          hosting121.com                  │
│ SFTP PORT:               22 (SSH) / 21 (FTP)            │
│ REMOTE DIRECTORY:        /home/121xml/public_html        │
│ SSL:                     AutoSSL (Let's Encrypt)        │
│ NAMESERVERS:             HostArmada Default              │
└─────────────────────────────────────────────────────────┘
```

---

## DEPLOYMENT OPTIONS

### **Option 1: Automated Deployment (Recommended)**

#### **For Linux/Mac:**
```bash
# 1. Navigate to project folder
cd F:\AI\Claude\Projects\121XML
# Or: cd /path/to/121xml

# 2. Make script executable
chmod +x DEPLOYMENT_SCRIPT.sh

# 3. Run deployment
./DEPLOYMENT_SCRIPT.sh

# The script will:
# ✓ Verify your local file
# ✓ Test SSH connection
# ✓ Create backup of existing files
# ✓ Upload website_index.html
# ✓ Rename to index.html
# ✓ Set correct permissions (644)
# ✓ Verify deployment
```

#### **For Windows (PowerShell):**
```powershell
# 1. Open PowerShell as Administrator
# 2. Navigate to project folder
cd "F:\AI\Claude\Projects\121XML"

# 3. Run deployment script
.\DEPLOY.bat

# OR use PowerShell version:
Set-Location "F:\AI\Claude\Projects\121XML"
.\DEPLOY_PowerShell.ps1
```

#### **For Windows (Git Bash):**
```bash
# 1. Open Git Bash
# 2. Navigate to project
cd "F:/AI/Claude/Projects/121XML"

# 3. Run deployment
bash DEPLOYMENT_SCRIPT.sh
```

---

### **Option 2: Manual cPanel File Manager**

**Step-by-step:**

1. **Log into cPanel:**
   - URL: `https://121xml.com:2083`
   - Username: `121xml`
   - Password: `[Your cPanel password]`

2. **Access File Manager:**
   - Click "File Manager"
   - Make sure "public_html" is selected
   - Click "Go"

3. **Upload website file:**
   - Click "Upload"
   - Select `website_index.html` from your computer
   - Wait for upload to complete

4. **Rename file:**
   - Right-click on `website_index.html`
   - Click "Rename"
   - Change to: `index.html`
   - Click "Rename"

5. **Set permissions:**
   - Right-click on `index.html`
   - Click "Change Permissions"
   - Set to: `644` (Read/Write for owner, Read for others)
   - Click "Change Permissions"

6. **Verify:**
   - Open browser
   - Visit: `https://121xml.com`
   - Should see your website!

---

### **Option 3: FTP Upload (FileZilla)**

**Setup FileZilla:**

1. **Download:** https://filezilla-project.org/download.php

2. **Connect:**
   - Host: `hosting121.com` (or your server IP)
   - Username: `121xml`
   - Password: `[Your cPanel password]`
   - Port: `21`
   - Click "Quickconnect"

3. **Navigate:**
   - Right side (Remote site): Find `public_html`
   - Double-click to enter

4. **Upload:**
   - Left side: Find `website_index.html`
   - Drag to right side (remote folder)
   - Wait for upload

5. **Rename:**
   - Right-click `website_index.html` (remote)
   - Click "Rename"
   - Change to: `index.html`

6. **Set permissions:**
   - Right-click `index.html`
   - Click "File permissions"
   - Set to: `644`
   - Click "OK"

---

### **Option 4: SFTP via SSH (Command Line)**

**If you prefer pure SSH:**

```bash
# Connect and upload in one command
scp -P 22 website_index.html 121xml@hosting121.com:~/public_html/

# Connect via SSH and finish
ssh -p 22 121xml@hosting121.com

# Once connected:
cd public_html
mv website_index.html index.html
chmod 644 index.html
ls -lh index.html
exit
```

---

## VERIFICATION CHECKLIST

After deployment, verify everything:

```bash
# 1. Test HTTP access
curl -I http://121xml.com
# Expected: HTTP/1.1 200 OK

# 2. Test HTTPS access
curl -I https://121xml.com
# Expected: HTTP/2 200 OK (after SSL certificate generates)

# 3. Test website content loads
curl https://121xml.com | head -20
# Should show HTML content

# 4. Check SSL certificate
openssl s_client -connect 121xml.com:443
# Should show certificate information

# 5. Test in browser
# Open: https://121xml.com
# All features should be interactive
# Check console for any JavaScript errors (F12)
```

**Or use online tools:**
- SSL Test: https://www.ssllabs.com/ssltest/analyze.html?d=121xml.com
- HTTP Status: https://httpstatus.io/121xml.com
- Performance: https://pagespeed.web.dev/

---

## TROUBLESHOOTING

### **Problem: "Permission Denied" error during upload**

**Solution:**
```bash
# Check file permissions
ls -la website_index.html

# Should be readable (644 minimum)
chmod 644 website_index.html

# Try upload again
```

---

### **Problem: Website shows "404 Not Found"**

**Solution:**
```bash
# Verify file is in public_html
ssh 121xml@hosting121.com
cd public_html
ls -la index.html

# File should exist as index.html
# If it doesn't, rename it:
mv website_index.html index.html
```

---

### **Problem: HTTPS shows "Certificate Error"**

**Solution:**
- This is normal during AutoSSL setup
- AutoSSL takes 30 minutes to generate certificate
- Wait 30 minutes, then refresh browser
- Force refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

**To manually trigger AutoSSL in cPanel:**
1. Go to cPanel
2. Click "SSL/TLS" or "AutoSSL"
3. Click "Run AutoSSL"
4. Wait 5-10 minutes

---

### **Problem: JavaScript features not working**

**Solution:**
```bash
# Check browser console for errors (F12)
# Verify correct file was uploaded
curl -I https://121xml.com

# Check server logs
ssh 121xml@hosting121.com
tail -50 logs/access_log
tail -50 logs/error_log
```

---

### **Problem: Website is blank or shows error**

**Solution:**
1. Check if `index.html` exists in public_html
2. Verify file size (should be ~50KB for website_index.html)
3. Check file permissions (should be 644)
4. Try uploading again

```bash
ssh 121xml@hosting121.com
cd public_html
ls -lh index.html
file index.html
head -10 index.html
```

---

## POST-DEPLOYMENT SETUP

### **1. Enable Gzip Compression (Performance)**

In cPanel → "Apache Handlers" or add to `.htaccess`:

```apache
# Enable gzip compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html
  AddOutputFilterByType DEFLATE text/plain
  AddOutputFilterByType DEFLATE text/xml
  AddOutputFilterByType DEFLATE application/json
</IfModule>
```

---

### **2. Set Cache Headers (Performance)**

Add to `.htaccess`:

```apache
# Browser cache for static files
<FilesMatch "\.html$">
  Header set Cache-Control "max-age=3600"
</FilesMatch>

<FilesMatch "\.(jpg|jpeg|png|gif|css|js|ico)$">
  Header set Cache-Control "max-age=86400"
</FilesMatch>
```

---

### **3. Enable GZIP in cPanel**

1. cPanel → "Optimize Website" or "Module Installers"
2. Make sure mod_deflate is enabled
3. Verify with: `curl -H "Accept-Encoding: gzip" -I https://121xml.com`

---

### **4. Set Up Monitoring**

Monitor uptime and performance:

**Option A: cPanel Uptime Monitor**
1. cPanel → "Uptime Monitor"
2. Add: `https://121xml.com`
3. Check frequency: Every 5 minutes

**Option B: Google Analytics**
1. Get Google Analytics ID
2. Add to website (if desired):
```html
<!-- Add before </head> tag -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_ID');
</script>
```

---

## FUTURE DEPLOYMENTS

### **Updating website (next versions):**

```bash
# Quick update - just re-run deployment script
./DEPLOYMENT_SCRIPT.sh
# OR
./DEPLOY.bat

# The script will:
# - Create backup of existing version
# - Upload new version
# - Automatically activate it
```

### **When ready to add Python backend:**

1. Create subdomain: `api.121xml.com`
2. Deploy Python files there
3. Update website to call: `https://api.121xml.com/...`

See: **DEPLOYMENT_AND_GETTING_STARTED.md** for Python backend setup

---

## SUPPORT CONTACTS

**HostArmada Support:**
- Portal: https://hosting121.com/portal
- Support: https://hosting121.com/support
- Knowledge Base: https://hosting121.com/kb

**Domain Issues:**
- Where registered? (GoDaddy, Namecheap, etc.)
- Check nameserver settings point to HostArmada

**SSL Issues:**
- cPanel → "SSL/TLS" → Run AutoSSL
- Wait 30 minutes for certificate generation

**Performance Issues:**
- cPanel → "Optimize Website"
- Enable: Gzip, Cache, Images Optimization

---

## SECURITY CHECKLIST

- [x] SSL/HTTPS enabled (AutoSSL)
- [x] Strong cPanel password (if default, change it!)
- [x] File permissions correct (644)
- [x] .htaccess protection (optional)
- [x] Regular backups enabled
- [x] Monitor uptime

---

## NEXT STEPS

1. **Choose deployment method above**
2. **Run deployment (manual or automated)**
3. **Verify website loads at https://121xml.com**
4. **Test interactive features**
5. **Check mobile responsiveness**
6. **Monitor logs for errors**
7. **When ready: Deploy Python backend to api.121xml.com**

---

**Status:** Ready for Deployment  
**Website:** https://121xml.com  
**Backend (Future):** https://api.121xml.com  
**Admin Panel:** https://121xml.com:2083 (cPanel)
