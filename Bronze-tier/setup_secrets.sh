#!/bin/bash

# 🔐 SETUP SECRETS SECURELY
# This script helps you configure credentials safely
# It creates a .env file and sets proper permissions

set -e  # Exit on error

echo "=========================================="
echo "🔐 AI Employee Vault - Secure Setup"
echo "=========================================="
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Create .env from template
echo "📝 Creating .env from template..."
cp .env.example .env
echo "✓ .env created"

# Get vault path
echo ""
echo "📁 Enter your AI Employee Vault path:"
echo "   (Example: /Users/yourname/AI_Employee_Vault)"
read -p "   Path: " VAULT_PATH

if [ ! -d "$VAULT_PATH" ]; then
    echo "❌ Error: Vault directory not found at: $VAULT_PATH"
    exit 1
fi

# Update VAULT_PATH in .env
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|VAULT_PATH=.*|VAULT_PATH=$VAULT_PATH|" .env
else
    # Linux
    sed -i "s|VAULT_PATH=.*|VAULT_PATH=$VAULT_PATH|" .env
fi

echo "✓ Vault path configured"

# Check for credentials file
echo ""
echo "🔐 Looking for credentials.json..."

CREDS_PATH="$VAULT_PATH/scripts/credentials.json"

if [ ! -f "$CREDS_PATH" ]; then
    echo ""
    echo "❌ credentials.json not found!"
    echo ""
    echo "📥 To get credentials:"
    echo "   1. Go to: https://console.cloud.google.com/apis/credentials"
    echo "   2. Create OAuth 2.0 Client ID (Desktop Application)"
    echo "   3. Download JSON and save as: $CREDS_PATH"
    echo ""
    read -p "Press Enter when ready..."

    if [ ! -f "$CREDS_PATH" ]; then
        echo "❌ Still can't find credentials.json. Exiting."
        exit 1
    fi
fi

echo "✓ Found credentials.json at: $CREDS_PATH"

# Update credentials path in .env
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|GMAIL_CREDENTIALS_PATH=.*|GMAIL_CREDENTIALS_PATH=$CREDS_PATH|" .env
else
    sed -i "s|GMAIL_CREDENTIALS_PATH=.*|GMAIL_CREDENTIALS_PATH=$CREDS_PATH|" .env
fi

# Set permissions on sensitive files
echo ""
echo "🔒 Setting secure file permissions..."

chmod 600 "$CREDS_PATH"
echo "✓ credentials.json: 600 (owner read/write only)"

if [ -f "$VAULT_PATH/scripts/token.json" ]; then
    chmod 600 "$VAULT_PATH/scripts/token.json"
    echo "✓ token.json: 600 (owner read/write only)"
fi

chmod 600 .env
echo "✓ .env: 600 (owner read/write only)"

# Verify .gitignore
echo ""
echo "🛡️  Verifying .gitignore..."

if grep -q "\.env" .gitignore; then
    echo "✓ .env is in .gitignore"
else
    echo "⚠️  Adding .env to .gitignore..."
    echo ".env" >> .gitignore
fi

if grep -q "credentials.json" .gitignore; then
    echo "✓ credentials.json is in .gitignore"
else
    echo "⚠️  Adding credentials.json to .gitignore..."
    echo "credentials.json" >> .gitignore
fi

if grep -q "token.json" .gitignore; then
    echo "✓ token.json is in .gitignore"
else
    echo "⚠️  Adding token.json to .gitignore..."
    echo "token.json" >> .gitignore
fi

# Test the setup
echo ""
echo "🧪 Testing setup..."

# Source .env and test
export $(cat .env | xargs)

if [ -n "$VAULT_PATH" ]; then
    echo "✓ VAULT_PATH loaded: $VAULT_PATH"
else
    echo "❌ Error loading VAULT_PATH"
    exit 1
fi

if [ -f "$GMAIL_CREDENTIALS_PATH" ]; then
    echo "✓ GMAIL_CREDENTIALS_PATH valid: $GMAIL_CREDENTIALS_PATH"
else
    echo "❌ Error: GMAIL_CREDENTIALS_PATH not found"
    exit 1
fi

# Verify no credentials in .env
echo ""
echo "🔐 Final security check..."

if grep -q "client_secret" .env; then
    echo "❌ WARNING: Found 'client_secret' in .env - this should never be here!"
    echo "   The .env should only contain paths, not actual secrets."
    exit 1
else
    echo "✓ No hardcoded secrets in .env"
fi

# Success
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "   1. Review .env to ensure paths are correct:"
echo "      cat .env"
echo ""
echo "   2. Start the Gmail Watcher:"
echo "      export \$(cat .env | xargs)"
echo "      python3 scripts/gmail_watcher.py"
echo ""
echo "   3. Or use the helper script:"
echo "      source run_with_secrets.sh"
echo ""
echo "🔐 Security reminders:"
echo "   • NEVER commit .env to git"
echo "   • NEVER share .env with anyone"
echo "   • Delete .env from shared machines"
echo "   • Rotate credentials monthly"
echo ""
echo "📖 For more info: cat SECURITY.md"
echo "=========================================="
