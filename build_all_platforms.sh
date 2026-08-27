#!/bin/bash
# 121AI Multi-Platform Build Script
# Builds 121AI for Windows, macOS, Linux, Web, iOS, Android

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUILD_DIR="$SCRIPT_DIR/build"
DIST_DIR="$BUILD_DIR/dist"
VERSION=$(python -c "exec(open('121ai/__version__.py').read()); print(__version__)")

echo "=================================================="
echo "121AI Multi-Platform Build"
echo "Version: $VERSION"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

build_web() {
    echo -e "${YELLOW}[1/7] Building Web Package${NC}"
    mkdir -p "$DIST_DIR/web"

    # Build Python wheel
    python -m build --wheel
    cp dist/121ai-*.whl "$DIST_DIR/web/"

    # Build Docker image
    docker build -t 121ai:latest -t 121ai:$VERSION .
    docker save 121ai:$VERSION | gzip > "$DIST_DIR/web/121ai-docker-$VERSION.tar.gz"

    echo -e "${GREEN}✓ Web build complete${NC}"
}

build_windows() {
    echo -e "${YELLOW}[2/7] Building Windows Package${NC}"

    if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
        echo -e "${RED}✗ Windows build requires Windows OS${NC}"
        return
    fi

    mkdir -p "$BUILD_DIR/windows"

    # Build Windows EXE
    pyinstaller \
        --name 121AI \
        --onefile \
        --windowed \
        --icon deployment/assets/121ai.ico \
        --add-data "121ai/ui:121ai/ui" \
        --add-data "121ai/config:121ai/config" \
        --distpath "$DIST_DIR/windows" \
        121ai/__main__.py

    # Create MSI installer
    if command -v wix &> /dev/null; then
        heat dir "$DIST_DIR/windows/121AI.exe" -o files.wxs
        candle.exe files.wxs -o "$BUILD_DIR/windows/files.wixobj"
        light.exe "$BUILD_DIR/windows/files.wixobj" -o "$DIST_DIR/windows/121AI-$VERSION.msi"
    fi

    echo -e "${GREEN}✓ Windows build complete${NC}"
}

build_macos() {
    echo -e "${YELLOW}[3/7] Building macOS Package${NC}"

    if [[ "$OSTYPE" != "darwin"* ]]; then
        echo -e "${RED}✗ macOS build requires macOS${NC}"
        return
    fi

    mkdir -p "$BUILD_DIR/macos"

    # Build macOS app
    pyinstaller \
        --name 121AI \
        --onefile \
        --windowed \
        --icon deployment/assets/121ai.icns \
        --osx-bundle-identifier com.121ai.app \
        --add-data "121ai/ui:121ai/ui" \
        --add-data "121ai/config:121ai/config" \
        --distpath "$DIST_DIR/macos" \
        121ai/__main__.py

    # Code sign
    if [ -n "$SIGNING_IDENTITY" ]; then
        codesign -s "$SIGNING_IDENTITY" -v "$DIST_DIR/macos/121AI.app"
    fi

    # Create DMG
    if command -v hdiutil &> /dev/null; then
        hdiutil create -volname "121AI" -srcfolder "$DIST_DIR/macos" -ov -format UDZO "$DIST_DIR/macos/121AI-$VERSION.dmg"
    fi

    echo -e "${GREEN}✓ macOS build complete${NC}"
}

build_linux() {
    echo -e "${YELLOW}[4/7] Building Linux Package${NC}"

    mkdir -p "$BUILD_DIR/linux"

    # Build Linux binary
    pyinstaller \
        --name 121AI \
        --onefile \
        --add-data "121ai/ui:121ai/ui" \
        --add-data "121ai/config:121ai/config" \
        --distpath "$DIST_DIR/linux" \
        121ai/__main__.py

    # Create AppImage (if appimagetool available)
    if command -v appimagetool &> /dev/null; then
        mkdir -p "$BUILD_DIR/AppDir/usr/bin"
        cp "$DIST_DIR/linux/121AI" "$BUILD_DIR/AppDir/usr/bin/"
        cp deployment/assets/121ai.png "$BUILD_DIR/AppDir/"

        APPIMAGE_PATH="$DIST_DIR/linux/121AI-$VERSION-x86_64.AppImage"
        appimagetool "$BUILD_DIR/AppDir" "$APPIMAGE_PATH"
        chmod +x "$APPIMAGE_PATH"
    fi

    echo -e "${GREEN}✓ Linux build complete${NC}"
}

build_ios() {
    echo -e "${YELLOW}[5/7] Building iOS Package${NC}"

    if [[ "$OSTYPE" != "darwin"* ]]; then
        echo -e "${RED}✗ iOS build requires macOS with Xcode${NC}"
        return
    fi

    mkdir -p "$BUILD_DIR/ios"

    # Check for briefcase
    if ! command -v briefcase &> /dev/null; then
        echo "Installing Briefcase..."
        pip install briefcase
    fi

    # Create Briefcase project
    cat > pyproject.toml << EOF
[build-system]
requires = ["briefcase"]

[tool.briefcase]
project_name = "121AI"
bundle = "com.121ai"
version = "1.0.0"
description = "Universal AI Orchestration Platform"
sources = ["121ai"]

[tool.briefcase.app.121ai]
formal_name = "121AI"
description = "Universal AI Orchestration Platform with Zero Vendor Lock-in"
bundle = "com.121ai"
version = "1.0.0"
url = "https://121ai.io"
license = "MIT"
author = "Rashad Khan"
author_email = "rashad@121.us"
requires = []

[tool.briefcase.app.121ai.ios]
requires = []
EOF

    briefcase build ios
    briefcase package ios

    # Copy to dist
    cp -r build/121ai/ios/build/121AI.ipa "$DIST_DIR/ios/121AI-$VERSION.ipa"

    echo -e "${GREEN}✓ iOS build complete${NC}"
}

build_android() {
    echo -e "${YELLOW}[6/7] Building Android Package${NC}"

    mkdir -p "$BUILD_DIR/android"

    # Check for buildozer
    if ! command -v buildozer &> /dev/null; then
        echo "Installing Buildozer..."
        pip install buildozer
    fi

    # Create buildozer spec
    cat > buildozer.spec << EOF
[app]
title = 121AI
package.name = 121ai
package.domain = com.121ai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,yaml
version = 1.0.0
requirements = python3,kivy,requests,openai,anthropic

[buildozer]
log_level = 2
warn_on_root = 1

[buildozer.sections]
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[app.permissions]
INTERNET = 1
ACCESS_NETWORK_STATE = 1
WRITE_EXTERNAL_STORAGE = 1
READ_EXTERNAL_STORAGE = 1
EOF

    buildozer android debug

    # Copy to dist
    cp bin/121ai-1.0.0-debug.apk "$DIST_DIR/android/121AI-$VERSION-debug.apk"

    echo -e "${GREEN}✓ Android build complete${NC}"
}

build_docker() {
    echo -e "${YELLOW}[7/7] Building Docker Image${NC}"

    mkdir -p "$DIST_DIR/docker"

    docker build \
        -t 121ai:latest \
        -t 121ai:$VERSION \
        -f deployment/Dockerfile \
        .

    docker save 121ai:$VERSION | gzip > "$DIST_DIR/docker/121ai-$VERSION.tar.gz"

    echo -e "${GREEN}✓ Docker build complete${NC}"
}

# Main build process
echo ""
echo "Select build target(s):"
echo "1. All platforms"
echo "2. Web only"
echo "3. Windows"
echo "4. macOS"
echo "5. Linux"
echo "6. iOS"
echo "7. Android"
echo "8. Docker"
read -p "Enter choice(s) [1-8, comma-separated]: " choice

case $choice in
    1)
        build_web
        build_windows
        build_macos
        build_linux
        build_ios
        build_android
        build_docker
        ;;
    2)
        build_web
        ;;
    3)
        build_windows
        ;;
    4)
        build_macos
        ;;
    5)
        build_linux
        ;;
    6)
        build_ios
        ;;
    7)
        build_android
        ;;
    8)
        build_docker
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo -e "${GREEN}✓ 121AI Build Complete!${NC}"
echo "=================================================="
echo ""
echo "Build outputs in: $DIST_DIR/"
echo ""
echo "Outputs:"
ls -lh "$DIST_DIR"/ 2>/dev/null || echo "No outputs generated"
echo ""
echo "Next steps:"
echo "1. Test builds locally"
echo "2. Sign binaries (Windows, macOS, iOS)"
echo "3. Create release notes"
echo "4. Push to GitHub Releases"
echo "5. Deploy to app stores (iOS App Store, Google Play, etc.)"
echo ""
