#!/bin/bash

# Heroku release script for uv projects
# This script will be run before your main process

echo "🔧 Heroku Release: Installing uv and dependencies..."

# Install uv
pip install uv

# Install dependencies using uv
uv sync --frozen

echo "✅ Dependencies installed successfully!"
