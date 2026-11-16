#!/usr/bin/env bash
# Compile CSS & starts app Flask be_aware.

set -euo pipefail  

PROJECT_DIR="/home/etv/code_projects/python/flask/be_aware"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo ">> Compiling CSS (Jinja pages)..."
cd "$FRONTEND_DIR"
npm run build:css

echo ">> Building the React app (served at /app)..."
npm run build

echo ">> Starting  be_aware..."
cd "$PROJECT_DIR"
python "$PROJECT_DIR/run.py"
