#!/bin/bash

# 🔐 RUN WATCHER WITH SECURE SECRETS
# This script loads .env and runs the Gmail Watcher safely

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "To set up secrets, run:"
    echo "   bash setup_secrets.sh"
    echo ""
    echo "Or create .env manually:"
    echo "   cp .env.example .env"
    echo "   nano .env  # Edit with your actual paths"
    exit 1
fi

# Load environment variables from .env
echo "🔐 Loading environment variables from .env..."
export $(cat .env | xargs)

# Verify credentials path
if [ ! -f "$GMAIL_CREDENTIALS_PATH" ]; then
    echo "❌ Error: Credentials not found at: $GMAIL_CREDENTIALS_PATH"
    echo ""
    echo "Check your .env file:"
    echo "   cat .env"
    exit 1
fi

# Verify vault path
if [ ! -d "$VAULT_PATH" ]; then
    echo "❌ Error: Vault directory not found at: $VAULT_PATH"
    echo ""
    echo "Check your .env file:"
    echo "   cat .env"
    exit 1
fi

echo "✓ Environment loaded"
echo "  Vault: $VAULT_PATH"
echo "  Credentials: $GMAIL_CREDENTIALS_PATH"
echo ""

# Navigate to scripts folder and run
cd "AI_Employee_Vault/scripts"

echo "🚀 Starting Gmail Watcher..."
echo "Press Ctrl+C to stop"
echo ""

python3 gmail_watcher.py "$VAULT_PATH"
