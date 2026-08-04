#!/bin/bash
set -e

# Save current directory (which is the Vercel project root)
PROJECT_DIR=$PWD
echo "Starting Vercel Build in $PROJECT_DIR"

# Install Flutter for Vercel
cd /tmp
if [ -d "flutter" ]; then
    echo "Flutter already exists in /tmp"
else
    git clone https://github.com/flutter/flutter.git -b stable
fi
export PATH="$PATH:/tmp/flutter/bin"

# Build Flutter Web App
cd $PROJECT_DIR
flutter pub get

# Default API URL if not set in Vercel dashboard
SAFE_API_URL="${API_BASE_URL:-http://127.0.0.1:8000/api/v1}"
echo "Building Flutter Web with API: $SAFE_API_URL"

flutter build web --release --dart-define=API_BASE_URL="$SAFE_API_URL"

echo "Build complete. Output directory contents:"
ls -la build/web
