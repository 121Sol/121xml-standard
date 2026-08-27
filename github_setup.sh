#!/bin/bash
# 121AI GitHub Repository Setup Script
# Run this script with your GitHub credentials to create and initialize the 121AI repo

set -e

echo "=================================================="
echo "121AI GitHub Repository Setup"
echo "=================================================="
echo ""

# Prompt for GitHub credentials
read -p "GitHub Username (rashadkhan4mna): " GITHUB_USER
GITHUB_USER=${GITHUB_USER:-rashadkhan4mna}

read -p "GitHub Email (rashadkhan4mna@gmail.com): " GITHUB_EMAIL
GITHUB_EMAIL=${GITHUB_EMAIL:-rashadkhan4mna@gmail.com}

read -sp "GitHub Personal Access Token (https://github.com/settings/tokens): " GITHUB_TOKEN
echo ""

REPO_NAME="121ai"
REPO_URL="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo ""
echo "Creating repository: $REPO_NAME"
echo "GitHub User: $GITHUB_USER"
echo ""

# Step 1: Create GitHub repository via API
echo "[1/6] Creating GitHub repository via API..."
curl -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"121AI - Universal AI Orchestration Platform\",\"private\":true,\"auto_init\":false}" \
  https://api.github.com/user/repos

if [ $? -eq 0 ]; then
    echo "✓ GitHub repository created successfully"
else
    echo "✗ Failed to create GitHub repository"
    exit 1
fi

# Step 2: Initialize local git repository
echo "[2/6] Initializing local git repository..."
cd /tmp
rm -rf 121ai-setup 2>/dev/null || true
mkdir -p 121ai-setup
cd 121ai-setup

git init
git config user.email "$GITHUB_EMAIL"
git config user.name "$GITHUB_USER"

echo "✓ Git repository initialized"

# Step 3: Copy source files
echo "[3/6] Copying 121AI source code..."
cp -r F:/AI/Claude/Projects/121XML/121ai-source/* . 2>/dev/null || echo "Note: Source code will be added after generation"
cp -r F:/AI/Claude/Projects/121XML/121XML_AI_OS_MASTER_SPEC.md . 2>/dev/null || true
cp -r F:/AI/Claude/Projects/121XML/121XML_PRINCIPLES_SECURITY_SOVEREIGNTY.md . 2>/dev/null || true
cp -r F:/AI/Claude/Projects/121XML/121XML_ARCHITECTURE_MEMORY_DETERMINISM.md . 2>/dev/null || true
cp -r F:/AI/Claude/Projects/121XML/121XML_GITHUB_STRATEGY.md . 2>/dev/null || true
cp -r F:/AI/Claude/Projects/121XML/121AI_LOGO.svg . 2>/dev/null || true
cp -r F:/AI/Claude/Projects/121XML/121AI_BROCHURE.html . 2>/dev/null || true
cp -r F:/AI/Claude/Projects/121XML/121AI_BUSINESS_CASE.md . 2>/dev/null || true
cp -r F:/AI/Claude/Projects/121XML/121AI_BRAND_GUIDELINES.md . 2>/dev/null || true

echo "✓ Source files copied"

# Step 4: Create .gitignore
echo "[4/6] Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
venv/
env/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Secrets
.env
.env.local
secrets.yaml
config.local.yml

# Build outputs
*.apk
*.ipa
*.dmg
*.exe
*.whl

# Logs
*.log
logs/

# Test coverage
.coverage
htmlcov/

# Node (for web UI)
node_modules/
npm-debug.log
yarn-error.log

# Docker
docker-compose.override.yml
.dockerignore

# IDE
.vscode/
.idea/
*.sublime-project
*.sublime-workspace
EOF

echo "✓ .gitignore created"

# Step 5: Create initial commit
echo "[5/6] Creating initial commit..."
git add -A
git commit -m "Initial 121AI repository - Master Specifications and Brand Identity" --allow-empty

echo "✓ Initial commit created"

# Step 6: Push to GitHub
echo "[6/6] Pushing to GitHub..."
git remote add origin "$REPO_URL"
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✓ Repository pushed to GitHub successfully"
else
    echo "✗ Failed to push to GitHub"
    exit 1
fi

echo ""
echo "=================================================="
echo "✓ 121AI GitHub Repository Setup Complete!"
echo "=================================================="
echo ""
echo "Repository URL: https://github.com/$GITHUB_USER/$REPO_NAME"
echo "Repository Path: /tmp/121ai-setup"
echo ""
echo "Next steps:"
echo "1. Clone the repository: git clone https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo "2. Copy source code: cp -r 121ai-source/* ."
echo "3. Create branches: git checkout -b develop"
echo "4. Start development with: python -m pip install -e ."
echo ""
