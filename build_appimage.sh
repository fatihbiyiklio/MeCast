#!/bin/bash
set -e

# Define variables
APP_NAME="MeCast"
APP_DIR="AppDir"
DIST_DIR="dist"
BUILD_DIR="build"
ICON_PATH="ui/icon.png"

# Ensure we are in the project root
cd "$(dirname "$0")"

# Activate venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run install.sh first or create a venv."
    exit 1
fi

# 1. Clean previous builds
echo "Cleaning previous builds..."
rm -rf "$APP_DIR" "$DIST_DIR" "$BUILD_DIR"

# 2. Build with PyInstaller
echo "Building with PyInstaller..."
pyinstaller MeCast.spec

# 3. Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APP_DIR/usr/share/applications"

# Copy binary
# cp "$DIST_DIR/$APP_NAME/$APP_NAME" "$APP_DIR/usr/bin/"
# Copy internal directories (if PyInstaller didn't bundle them into the executable, but MeCast.spec seems to bundle them into the dist folder. 
# Since we are using a directory based build in spec (onedir is default if not specified as onefile), we need to copy the whole folder content or use onefile.
# Let's check MeCast.spec again. It uses EXE but doesn't explicitly say COLLECT. 
# Wait, the spec file provided earlier has `exe = EXE(pyz, a.scripts, a.binaries, a.datas, ...)` which implies ONEFILE mode because it includes binaries and datas in EXE.
# If it's onefile, we just copy the single executable.

# Let's verify if it is onefile.
# The spec file has `a.binaries, a.datas` inside EXE, and `exclude_binaries=True` is NOT present (default is False, but usually for onedir we see COLLECT).
# Actually, standard onedir spec has `exe = EXE(..., exclude_binaries=True, ...)` and then `coll = COLLECT(...)`.
# The provided spec has everything in EXE, so it IS onefile.
# So `dist/MeCast` will be a single file (or `dist/MeCast.exe` on Windows, but here Linux).

# Copy the executable
cp "$DIST_DIR/$APP_NAME" "$APP_DIR/usr/bin/$APP_NAME"

# Copy icon
if [ -f "$ICON_PATH" ]; then
    cp "$ICON_PATH" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"
    cp "$ICON_PATH" "$APP_DIR/$APP_NAME.png" # AppImage requires icon in root of AppDir too usually, or .DirIcon
else
    echo "Warning: Icon not found at $ICON_PATH"
    # Create a dummy icon if needed or fail? Let's just warn.
fi

# Create desktop file
echo "Creating desktop file..."
cat > "$APP_DIR/$APP_NAME.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$APP_NAME
Comment=Android Screen Mirroring Tool
Exec=$APP_NAME
Icon=$APP_NAME
Categories=Utility;
Terminal=false
EOF

# Create AppRun
echo "Creating AppRun..."
cat > "$APP_DIR/AppRun" <<EOF
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
export PATH="\${HERE}/usr/bin:\${PATH}"
export LD_LIBRARY_PATH="\${HERE}/usr/lib:\${LD_LIBRARY_PATH}"
exec "\${HERE}/usr/bin/$APP_NAME" "\$@"
EOF
chmod +x "$APP_DIR/AppRun"

# 4. Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# 5. Generate AppImage
echo "Generating AppImage..."
# We need to set ARCH for appimagetool sometimes
export ARCH=x86_64
./appimagetool-x86_64.AppImage "$APP_DIR"

echo "Build complete!"
