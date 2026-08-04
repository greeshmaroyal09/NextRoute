import os

RENDER_YAML = '''services:
  - type: web
    name: nextroute-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -c gunicorn.conf.py app.main:app
    envVars:
      - key: ENVIRONMENT
        value: prod
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        sync: false # Set securely in Render dashboard
      - key: REDIS_URL
        sync: false # Set securely in Render dashboard
      - key: SECRET_KEY
        generateValue: true
      - key: CORS_ORIGINS
        value: '["*"]' # Update this securely in Render dashboard
'''

PROCFILE = '''web: gunicorn -c gunicorn.conf.py app.main:app
'''

VERCEL_JSON = '''{
  "buildCommand": "./build_vercel.sh",
  "outputDirectory": "build/web",
  "framework": null,
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
'''

BUILD_VERCEL_SH = '''#!/bin/bash
# Install Flutter for Vercel
cd /tmp
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:/tmp/flutter/bin"

# Build Flutter Web App
cd $VERCEL_GIT_REPO_SLUG/frontend
flutter pub get
flutter build web --release --dart-define=API_BASE_URL=$API_BASE_URL
'''

def write_files():
    # Render configuration (can be at root for monorepos or inside backend)
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(RENDER_YAML)
    
    with open('backend/Procfile', 'w', encoding='utf-8') as f:
        f.write(PROCFILE)
        
    # Update requirements.txt
    req_path = 'backend/requirements.txt'
    if os.path.exists(req_path):
        with open(req_path, 'a', encoding='utf-8') as f:
            f.write("\ngunicorn>=21.2.0\n")
            
    # Vercel configuration
    with open('frontend/vercel.json', 'w', encoding='utf-8') as f:
        f.write(VERCEL_JSON)
        
    with open('frontend/build_vercel.sh', 'w', encoding='utf-8') as f:
        f.write(BUILD_VERCEL_SH)
        
    # Make build script executable (for unix systems)
    try:
        os.chmod('frontend/build_vercel.sh', 0o755)
    except:
        pass

    print("Cloud deployment configurations generated successfully.")

if __name__ == "__main__":
    write_files()
