#!/bin/bash

# ============================================================================
# 121XML Website Deployment Script
# Deploy to HostArmada cPanel - hosting121.com
# ============================================================================

set -e  # Exit on error

# Configuration - EDIT THESE
CPANEL_USER="121xml"                    # Your cPanel username
SERVER="hosting121.com"                 # Your HostArmada server
DOMAIN="121xml.com"                     # Your domain
SSH_PORT="22"                           # SSH port (usually 22)
SOURCE_FILE="website_index.html"        # Local file to upload
REMOTE_PATH="public_html"               # Remote directory

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║       121XML Website Deployment to HostArmada                  ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"

# Step 1: Verify local file exists
echo -e "\n${YELLOW}[Step 1/5]${NC} Verifying source file..."
if [ ! -f "$SOURCE_FILE" ]; then
    echo -e "${RED}✗ Error: $SOURCE_FILE not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Source file found${NC}"
FILE_SIZE=$(du -h "$SOURCE_FILE" | cut -f1)
echo "  File size: $FILE_SIZE"

# Step 2: Test SSH connection
echo -e "\n${YELLOW}[Step 2/5]${NC} Testing SSH connection to $SERVER..."
if ! ssh -p $SSH_PORT -o ConnectTimeout=5 "${CPANEL_USER}@${SERVER}" "echo 'SSH connection OK'" > /dev/null 2>&1; then
    echo -e "${RED}✗ Cannot connect to SSH${NC}"
    echo "  Check your credentials and server address"
    exit 1
fi
echo -e "${GREEN}✓ SSH connection successful${NC}"

# Step 3: Create backup of existing index.html (if exists)
echo -e "\n${YELLOW}[Step 3/5]${NC} Creating backup of existing files..."
BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
ssh -p $SSH_PORT "${CPANEL_USER}@${SERVER}" << BACKUP_EOF
if [ -f "$REMOTE_PATH/index.html" ]; then
    mkdir -p "$BACKUP_DIR"
    cp "$REMOTE_PATH/index.html" "$BACKUP_DIR/index.html.bak"
    echo "✓ Backup created: $BACKUP_DIR/index.html.bak"
else
    echo "✓ No existing index.html to backup"
fi
BACKUP_EOF

# Step 4: Upload website file
echo -e "\n${YELLOW}[Step 4/5]${NC} Uploading website file..."
scp -P $SSH_PORT "$SOURCE_FILE" "${CPANEL_USER}@${SERVER}:${REMOTE_PATH}/website_index.html"
echo -e "${GREEN}✓ File uploaded${NC}"

# Step 5: Deploy (rename to index.html and set permissions)
echo -e "\n${YELLOW}[Step 5/5]${NC} Finalizing deployment..."
ssh -p $SSH_PORT "${CPANEL_USER}@${SERVER}" << DEPLOY_EOF
#!/bin/bash
set -e

# Navigate to public_html
cd ~/$REMOTE_PATH

# Rename file
mv website_index.html index.html

# Set correct permissions
chmod 644 index.html

# Verify
if [ -f "index.html" ]; then
    echo "✓ File deployed successfully"
    ls -lh index.html
else
    echo "✗ Deployment failed"
    exit 1
fi
DEPLOY_EOF

# Verification
echo -e "\n${YELLOW}Verifying deployment...${NC}"
sleep 2

# Check HTTP response
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Website is accessible (HTTP 200)${NC}"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✓ Website redirects correctly (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Got HTTP $HTTP_CODE (may still be propagating)${NC}"
fi

# Check HTTPS
HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" 2>/dev/null || echo "000")
if [ "$HTTPS_CODE" = "200" ]; then
    echo -e "${GREEN}✓ HTTPS is working (HTTP 200)${NC}"
else
    echo -e "${YELLOW}⚠ HTTPS not yet available (may be generating certificate)${NC}"
fi

# Final summary
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            ✓ DEPLOYMENT SUCCESSFUL                              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}Your website is live at:${NC}"
echo -e "  ${GREEN}https://$DOMAIN${NC}"
echo -e "  ${GREEN}http://$DOMAIN${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Visit https://$DOMAIN in your browser"
echo -e "  2. Test the interactive features"
echo -e "  3. Check mobile responsiveness"
echo -e "  4. Set up Google Analytics (optional)"
echo -e "  5. Configure SEO metadata (optional)"

echo -e "\n${YELLOW}Backup information:${NC}"
echo -e "  Backups stored in: $BACKUP_DIR"
echo -e "  To restore: ssh ${CPANEL_USER}@${SERVER}"
echo -e "             cp $BACKUP_DIR/index.html.bak $REMOTE_PATH/index.html"

echo -e "\n${YELLOW}Support:${NC}"
echo -e "  Documentation: See DEPLOYMENT_AND_GETTING_STARTED.md"
echo -e "  Issues: Check cPanel File Manager for permissions"
echo -e "  SSL: AutoSSL usually activates within 30 minutes\n"
