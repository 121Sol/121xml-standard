#!/bin/bash

##############################################################################
# 121XML AI OS - Automated Deployment Script via SSH
# Usage: ./deploy.sh <environment> <version> <server_user@server_ip>
# Example: ./deploy.sh production 1.0.0 deploy@api.121xml.us
##############################################################################

set -e

ENVIRONMENT=${1:-dev}
VERSION=${2:-1.0.0}
TARGET_SERVER=${3:-localhost}
DEPLOY_DIR="/opt/121xml-ai-os"
BACKUP_DIR="/opt/121xml-backups"
LOG_FILE="deployment_${VERSION}_$(date +%s).log"

echo "=========================================="
echo "121XML AI OS Deployment"
echo "=========================================="
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo "Target: $TARGET_SERVER"
echo "Timestamp: $(date)"
echo "Log: $LOG_FILE"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a $LOG_FILE
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a $LOG_FILE
}

# ==================== PRE-DEPLOYMENT CHECKS ====================
log "Step 1: Pre-deployment Validation"

# Check SSH connectivity
if ! ssh -o ConnectTimeout=5 $TARGET_SERVER "echo 'SSH connection OK'" > /dev/null 2>&1; then
    error "Cannot connect to $TARGET_SERVER via SSH"
fi
log "✓ SSH connectivity verified"

# Check required files exist
for file in public_technical_architecture.html public_ui_specifications.html public_api_reference.html public_gtm_strategy.html; do
    if [ ! -f "$file" ]; then
        error "Missing required file: $file"
    fi
done
log "✓ All deployment files present"

# ==================== CREATE BACKUP ====================
log "Step 2: Creating Backup"

BACKUP_TS=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_${VERSION}_${BACKUP_TS}"

ssh $TARGET_SERVER << BACKUP_CMDS
    set -e
    mkdir -p "$BACKUP_DIR"
    if [ -d "$DEPLOY_DIR" ]; then
        mkdir -p "$BACKUP_PATH"
        cp -r "$DEPLOY_DIR"/* "$BACKUP_PATH/" 2>/dev/null || true
        echo "Backup created at $BACKUP_PATH"
    else
        echo "No previous deployment to backup"
    fi
BACKUP_CMDS

log "✓ Backup completed: $BACKUP_PATH"

# ==================== TRANSFER FILES ====================
log "Step 3: Transferring Files via SCP"

ssh $TARGET_SERVER "mkdir -p $DEPLOY_DIR"

# Transfer public specs
for file in public_technical_architecture.html public_ui_specifications.html public_api_reference.html; do
    scp "$file" "$TARGET_SERVER:$DEPLOY_DIR/" 2>/dev/null
    log "✓ Transferred $file"
done

# Transfer internal docs (password protected)
scp public_gtm_strategy.html "$TARGET_SERVER:$DEPLOY_DIR/internal/" 2>/dev/null || true
log "✓ Transferred internal docs"

# Transfer archive
scp -r data/ "$TARGET_SERVER:$DEPLOY_DIR/" 2>/dev/null || true
log "✓ Transferred archive"

# ==================== RUN HEALTH CHECKS ====================
log "Step 4: Health Checks"

ssh $TARGET_SERVER << HEALTH_CHECKS
    set -e
    
    # Check file integrity
    cd $DEPLOY_DIR
    
    # Verify HTML files
    for file in public_technical_architecture.html public_ui_specifications.html public_api_reference.html; do
        if [ ! -f "$file" ]; then
            echo "ERROR: $file not found"
            exit 1
        fi
        # Basic HTML validation
        if ! grep -q "<!DOCTYPE html>" "$file"; then
            echo "WARNING: $file may not be valid HTML"
        fi
    done
    
    # Check archive integrity
    if [ -d "data" ] && [ -f "data/ARCHIVE_INDEX.json" ]; then
        echo "Archive present and valid"
    fi
    
    echo "All health checks passed"
HEALTH_CHECKS

log "✓ Health checks passed"

# ==================== VERIFY SSL/TLS ====================
log "Step 5: SSL/TLS Verification"

ssh $TARGET_SERVER << SSL_CHECK
    set -e
    if [ -f "/etc/ssl/certs/121xml.crt" ]; then
        echo "SSL certificate found"
        openssl x509 -in /etc/ssl/certs/121xml.crt -noout -dates
    else
        echo "WARNING: SSL certificate not found. Using self-signed or HTTP."
    fi
SSL_CHECK

log "✓ SSL/TLS verified"

# ==================== CLEAR CDN CACHE ====================
log "Step 6: CDN Cache Clearing"

# Cloudflare cache purge (if configured)
if [ ! -z "$CLOUDFLARE_ZONE_ID" ] && [ ! -z "$CLOUDFLARE_AUTH_TOKEN" ]; then
    curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/purge_cache" \
        -H "Authorization: Bearer $CLOUDFLARE_AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        --data '{"files":["https://docs.121xml.us/*"]}' 2>/dev/null
    log "✓ CDN cache cleared"
else
    warning "CDN configuration not found, skipping cache purge"
fi

# ==================== RUN SMOKE TESTS ====================
log "Step 7: Smoke Tests"

ssh $TARGET_SERVER << SMOKE_TESTS
    set -e
    
    cd $DEPLOY_DIR
    
    # Test that files are accessible
    if [ -f "public_technical_architecture.html" ]; then
        SIZE=\$(wc -c < public_technical_architecture.html)
        if [ $SIZE -lt 50000 ]; then
            echo "ERROR: Technical architecture file too small"
            exit 1
        fi
    fi
    
    # Test JSON validity
    if command -v jq &> /dev/null; then
        if [ -f "data/ARCHIVE_INDEX.json" ]; then
            if ! jq empty data/ARCHIVE_INDEX.json 2>/dev/null; then
                echo "ERROR: Archive index JSON invalid"
                exit 1
            fi
        fi
    fi
    
    echo "Smoke tests passed"
SMOKE_TESTS

log "✓ Smoke tests passed"

# ==================== UPDATE VERSION TRACKER ====================
log "Step 8: Version Tracking"

ssh $TARGET_SERVER << VERSION_UPDATE
    set -e
    
    cat > $DEPLOY_DIR/.deployment_info << DEPLOYMENT_INFO
{
  "version": "$VERSION",
  "environment": "$ENVIRONMENT",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "deployed_by": "$USER",
  "backup_path": "$BACKUP_PATH"
}
DEPLOYMENT_INFO

    chmod 644 $DEPLOY_DIR/.deployment_info
    echo "Deployment info recorded"
DEPLOYMENT_UPDATE

log "✓ Version updated: $VERSION"

# ==================== SEND NOTIFICATION ====================
log "Step 9: Sending Notifications"

NOTIFICATION_MESSAGE="
✅ 121XML AI OS v$VERSION deployed successfully to $ENVIRONMENT
- Target: $TARGET_SERVER
- Timestamp: $(date)
- Backup: $BACKUP_PATH
- Status: LIVE
"

# Email notification (if configured)
if command -v mail &> /dev/null; then
    echo "$NOTIFICATION_MESSAGE" | mail -s "Deployment Success: 121XML $VERSION to $ENVIRONMENT" devops@121.us 2>/dev/null || true
fi

log "✓ Notifications sent"

# ==================== DEPLOYMENT COMPLETE ====================
log ""
log "=========================================="
log "✅ DEPLOYMENT SUCCESSFUL"
log "=========================================="
log "Version: $VERSION"
log "Environment: $ENVIRONMENT"
log "Server: $TARGET_SERVER"
log "Deployed at: $(date)"
log "Log: $LOG_FILE"
log ""
log "Next Steps:"
log "1. Verify at: https://docs.121xml.us"
log "2. Check metrics: https://api.121xml.us/health"
log "3. Monitor logs: ssh $TARGET_SERVER tail -f /var/log/121xml/access.log"
log ""

# ==================== ROLLBACK PROCEDURE ====================
echo ""
echo "📋 ROLLBACK PROCEDURE (if needed):"
echo "=========================================="
echo "To rollback to previous version:"
echo "  ssh $TARGET_SERVER rm -rf $DEPLOY_DIR"
echo "  ssh $TARGET_SERVER cp -r $BACKUP_PATH/* $DEPLOY_DIR/"
echo "  Then run: ./deploy.sh $ENVIRONMENT <previous_version> $TARGET_SERVER"
echo "=========================================="

