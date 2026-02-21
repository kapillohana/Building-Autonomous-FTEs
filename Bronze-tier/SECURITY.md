# 🔐 Security Guide: Protecting Your Credentials

**Critical**: Your credentials are the keys to your AI Employee's kingdom. This guide shows you how to keep them safe.

---

## ⚠️ NEVER DO THIS

```bash
# ❌ BAD - Don't commit credentials to git
git add credentials.json
git commit -m "Add Gmail API credentials"

# ❌ BAD - Don't store passwords in code
GMAIL_PASSWORD = "mypassword123"

# ❌ BAD - Don't paste credentials in chat or email
"credentials": {"client_id": "abc123..."}

# ❌ BAD - Don't use weak passwords
password123
admin
mypassword
```

---

## ✅ DO THIS INSTEAD

### Step 1: Create a .env File (Keep It Local!)

```bash
# Copy the template
cp .env.example .env

# Edit .env with your actual credentials
# DO NOT commit this file - it's in .gitignore
nano .env
```

**Your .env file should look like:**
```bash
GMAIL_CREDENTIALS_PATH=./scripts/credentials.json
GMAIL_TOKEN_PATH=./scripts/token.json
VAULT_PATH=/Users/yourname/AI_Employee_Vault
LOG_LEVEL=INFO
```

### Step 2: Keep Credentials Out of Git

Check that `.gitignore` includes:
```
.env
credentials.json
token.json
```

Verify they won't be committed:
```bash
git status
# Should show:
# .env (not listed - means it's ignored ✓)
# credentials.json (not listed ✓)
```

### Step 3: Store Credentials Securely

#### Option A: Environment Variables (Recommended)
```bash
# Export before running
export GMAIL_CREDENTIALS_PATH="./scripts/credentials.json"
python3 scripts/gmail_watcher.py
```

#### Option B: OS Keychain (Mac)
```bash
# Store credential path in Keychain
security add-generic-password -s "gmail_creds" -a "watcher" -w "/path/to/credentials.json"

# Retrieve when needed
security find-generic-password -s "gmail_creds" -w
```

#### Option C: 1Password CLI (Professional)
```bash
# Requires 1Password subscription, but most secure
op read op://vault/Gmail\ API/credentials
```

#### Option D: Windows Credential Manager
```powershell
# Store in Windows Credential Manager
cmdkey /add:gmail_creds /user:watcher /pass:"path/to/credentials.json"
```

---

## 📋 Monthly Security Checklist

### Every Month:
- [ ] Verify `.gitignore` includes `.env`, `credentials.json`, `token.json`
- [ ] Check that no credentials appear in logs
- [ ] Review git history to ensure no accidental commits
- [ ] Rotate Gmail OAuth token (optional but recommended)

### Every 3 Months:
- [ ] Regenerate Google OAuth credentials
- [ ] Review permissions on `credentials.json` (should be 600)
- [ ] Update passwords if you've shared the machine
- [ ] Check logs for suspicious activity

### Annually:
- [ ] Full security audit
- [ ] Update all API credentials
- [ ] Review and update security policies

---

## 🔍 How to Rotate Gmail Credentials

### Step 1: Revoke Old Token
```bash
# Delete the old token
rm scripts/token.json

# Next time you run gmail_watcher.py, it will ask for new auth
python3 scripts/gmail_watcher.py
```

### Step 2: Regenerate Client Secret (If Needed)
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID
3. Delete the old one
4. Create a new one
5. Download and replace `scripts/credentials.json`

---

## 🛡️ Protecting credentials.json and token.json

### File Permissions (Linux/Mac)
```bash
# Make credentials readable only by you
chmod 600 scripts/credentials.json
chmod 600 scripts/token.json

# Verify
ls -la scripts/credentials.json
# Should show: -rw------- (owner read/write only)
```

### Windows
```powershell
# Right-click file → Properties → Security → Edit
# Remove "Everyone" and "Users" - only your account should access
```

---

## 🚨 If You Accidentally Commit Credentials

### Step 1: IMMEDIATELY Revoke THEM
```bash
# For Gmail: Delete the OAuth app and regenerate
# For API keys: Delete the key in the cloud console
```

### Step 2: Remove from Git History
```bash
# Option A: If not pushed yet
git reset HEAD^ --soft  # Undo last commit
rm credentials.json
git add -A
git commit -m "Remove credentials (before they were leaked)"

# Option B: If already pushed
# Use: git-filter-repo (more complex)
# See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
```

### Step 3: Alert Team (If Applicable)
- Notify anyone who might have accessed the git history
- Ask them to revoke any stolen tokens

---

## 🔑 Types of Secrets You'll Handle

### Gmail Credentials
- **Location**: `scripts/credentials.json`
- **Type**: OAuth 2.0 Client Secret
- **Risk**: Medium (can only access your Gmail account)
- **Rotation**: Quarterly or as needed
- **Storage**: .env file, never in code

### Gmail Token
- **Location**: `scripts/token.json`
- **Type**: Access Token + Refresh Token
- **Risk**: Medium (can access your Gmail)
- **Rotation**: Automatically rotates on refresh
- **Storage**: Local file, keep private

### Bank API Keys (Future)
- **Location**: .env only
- **Type**: API Key + Secret
- **Risk**: HIGH - Can access accounts
- **Rotation**: Monthly minimum
- **Storage**: OS Keychain or 1Password only

### WhatsApp Session (Future)
- **Location**: .env or secure folder
- **Type**: Browser session
- **Risk**: HIGH - Full account access
- **Rotation**: Annually
- **Storage**: Encrypted, local only

---

## 📊 Credential Risk Matrix

| Credential | Risk | Impact | Rotation |
|-----------|------|--------|----------|
| Gmail OAuth Token | Medium | Email access | Monthly |
| Bank API Key | HIGH | Financial access | Weekly |
| API Secrets | HIGH | Full service access | Monthly |
| WhatsApp Session | HIGH | Chat + contacts | Quarterly |

---

## 🔐 Best Practices Summary

### DO ✅
- Use `.env` file for local development
- Add `.env` to `.gitignore`
- Store credentials in OS Keychain (production)
- Use OAuth 2.0 where possible (safer than passwords)
- Rotate credentials monthly
- Use strong, unique passwords
- Enable 2FA on all accounts
- Keep file permissions restrictive (600)
- Monitor logs for suspicious access
- Document credential locations (securely)

### DON'T ❌
- Commit credentials to git
- Hardcode credentials in code
- Use weak passwords
- Share credentials in chat/email
- Store credentials in vault (Obsidian)
- Leave credentials in Terminal history
- Use same credential for multiple services
- Commit .env files
- Log full credential values
- Trust "temporary" secrets

---

## 🆘 Emergency: Leaked Credential

### Immediate Actions (Within Minutes):
1. **Stop the watcher**: Kill any running processes
2. **Revoke access**: Delete the compromised credential in cloud console
3. **Alert authorities**: If financial credentials leaked, contact your bank

### Follow-up (Within Hours):
1. **Generate new credentials**: Create new OAuth apps, API keys
2. **Update your setup**: Use new credentials in .env
3. **Scan logs**: Check for unauthorized access patterns
4. **Change passwords**: Update related accounts

### Long-term (Within Days):
1. **Enable 2FA**: Add two-factor authentication everywhere
2. **Monitor account**: Watch for suspicious activity
3. **Document incident**: Record what happened for future reference
4. **Update policies**: Adjust security practices to prevent repeat

---

## 📚 References

### Google OAuth Security
- https://developers.google.com/identity/protocols/oauth2/security-best-practices
- https://console.cloud.google.com/apis/credentials

### Environment Variables
- https://en.wikipedia.org/wiki/.env
- https://github.com/motdotla/dotenv

### Python Secrets Management
- https://pypi.org/project/python-dotenv/
- https://docs.python.org/3/library/secrets.html

### Git Security
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure
- https://git-scm.com/docs/gitignore

### Credential Managers
- **Mac**: Keychain (built-in)
- **Windows**: Credential Manager (built-in)
- **Cross-platform**: 1Password, Bitwarden, Dashlane
- **CLI**: 1Password CLI, vault

---

## ✨ Your Current Setup Status

### ✅ Already Protected:
- `.gitignore` created (blocks credential commits)
- `.env.example` template provided
- Credentials NOT in code

### ⚠️ Still TODO (To Be Fully Secure):
1. [ ] Create your `.env` file with actual paths
2. [ ] Test that credentials work via environment variables
3. [ ] Set file permissions: `chmod 600 scripts/credentials.json`
4. [ ] Remove credentials from any git history (if any commits)
5. [ ] Set up OS Keychain or 1Password for production

---

## 🚀 Next: Update gmail_watcher.py to Use .env

See the updated `scripts/gmail_watcher.py` which reads from environment variables instead of hardcoded paths.

Usage:
```bash
# Load .env and run
export $(cat .env | xargs)
python3 scripts/gmail_watcher.py
```

---

**Remember**: Credentials are the difference between a helpful AI Employee and a security disaster. Take this seriously! 🔐

---

*Last Updated: 2026-02-22*
*Part of Bronze Tier Security Hardening*