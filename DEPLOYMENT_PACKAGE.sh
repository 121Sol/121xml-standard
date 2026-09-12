#!/bin/bash
# © 2026 121 Solutions USA. All rights reserved.
#
# The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive
# property of 121 Solutions USA.
#
# Unauthorized use, reproduction, or distribution of this material,
# including any proprietary designs, software, or documentation, is
# strictly prohibited without prior written permission from 121 Solutions USA.
# 121XML Website Deployment Package
# ===================================
# This script deploys website_v3_complete.html to 121xml.com
# Run this on your production server or deployment automation

set -e

echo "🚀 121XML Website Deployment Started"
echo "===================================="

# Configuration
DOMAIN="121xml.com"
WEB_ROOT="/var/www/121xml"
BACKUP_DIR="/var/www/backups"
FILE_SOURCE="website_v3_complete.html"
FILE_DEST="index.html"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory if needed
mkdir -p "$BACKUP_DIR"

# Backup existing site (if it exists)
if [ -f "$WEB_ROOT/$FILE_DEST" ]; then
    echo "📦 Backing up existing site..."
    cp "$WEB_ROOT/$FILE_DEST" "$BACKUP_DIR/${FILE_DEST}.backup.${TIMESTAMP}"
    echo "✅ Backup created: $BACKUP_DIR/${FILE_DEST}.backup.${TIMESTAMP}"
else
    echo "ℹ️  No existing site found (fresh deployment)"
fi

# Create web root if needed
mkdir -p "$WEB_ROOT"

# Copy file
echo "📋 Copying website file..."
cp "$FILE_SOURCE" "$WEB_ROOT/$FILE_DEST"
echo "✅ File deployed to $WEB_ROOT/$FILE_DEST"

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 644 "$WEB_ROOT/$FILE_DEST"
chown www-data:www-data "$WEB_ROOT/$FILE_DEST" 2>/dev/null || true
echo "✅ Permissions set"

# Verify deployment
echo "✔️  Verifying deployment..."
if [ -f "$WEB_ROOT/$FILE_DEST" ]; then
    FILE_SIZE=$(stat -f%z "$WEB_ROOT/$FILE_DEST" 2>/dev/null || stat -c%s "$WEB_ROOT/$FILE_DEST")
    echo "✅ File verified: $FILE_SIZE bytes"
else
    echo "❌ Deployment failed: File not found at $WEB_ROOT/$FILE_DEST"
    exit 1
fi

# Test HTTP access (if curl available)
if command -v curl &> /dev/null; then
    echo "🌐 Testing HTTP access..."
    if curl -s "http://localhost/" | grep -q "121XML"; then
        echo "✅ Website is accessible and responsive"
    else
        echo "⚠️  Warning: Could not verify HTTP response"
    fi
fi

echo ""
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "===================================="
echo "Domain: $DOMAIN"
echo "Location: $WEB_ROOT/$FILE_DEST"
echo "File Size: ${FILE_SIZE:-check manually} bytes"
echo "Deployment Time: $TIMESTAMP"
echo "Backup: $BACKUP_DIR/${FILE_DEST}.backup.${TIMESTAMP}"
echo ""
echo "Next steps:"
echo "1. Verify site is live: https://$DOMAIN"
echo "2. Check all interactive features work"
echo "3. Test on mobile devices"
echo "4. Monitor analytics"
echo ""
echo "To rollback if needed:"
echo "cp $BACKUP_DIR/${FILE_DEST}.backup.${TIMESTAMP} $WEB_ROOT/$FILE_DEST"
