#!/usr/bin/env bash
# Builds the React app and starts the Flask app be_aware.

set -euo pipefail

PROJECT_DIR="/home/etv/code_projects/python/flask/be_aware"

echo ">> Building the React app (served by Flask at /)..."
cd "$PROJECT_DIR/frontend"
npm run build

echo ">> Starting be_aware..."
cd "$PROJECT_DIR/backend"
python run.py
