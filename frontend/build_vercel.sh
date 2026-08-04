#!/bin/bash
# Install Flutter for Vercel
cd /tmp
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:/tmp/flutter/bin"

# Build Flutter Web App
cd $VERCEL_GIT_REPO_SLUG/frontend
flutter pub get
flutter build web --release --dart-define=API_BASE_URL=$API_BASE_URL
