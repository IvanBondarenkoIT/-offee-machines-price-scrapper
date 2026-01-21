# Security Policy

## 🔒 Secrets Management

### What is committed to git:
- ✅ `generate_railway_keys.py` - Script to **generate** new keys (safe)
- ✅ `*.example.*` files - Templates without real secrets (safe)
- ✅ Documentation with example keys (safe - not real secrets)

### What is NEVER committed to git:
- ❌ `config.ini` - Contains real API keys (in `.gitignore`)
- ❌ `.env` - Contains real secrets (in `.gitignore`)
- ❌ Railway environment variables - Only in Railway dashboard

## 🛡️ How We Protect Secrets

### 1. Environment Variables (Production)
Real secrets are stored as **Railway environment variables**:
- `SECRET_KEY` - Flask session key
- `API_KEY` - API authentication
- `ADMIN_PASSWORD` - Admin user password
- `DATABASE_URL` - Database connection string

**These are ONLY in Railway, never in code.**

### 2. Local Development
For local development:
1. Copy `env.example.txt` to `.env`
2. Generate new keys: `python generate_railway_keys.py`
3. Add keys to `.env`
4. `.env` is in `.gitignore` and never committed

### 3. Config Files
- `config.ini` - Local uploader config (in `.gitignore`)
- `web_uploader/config.example.ini` - Template only (safe to commit)

## 🔑 Key Rotation

If you suspect a key has been compromised:

### Railway Keys:
1. Generate new keys: `python generate_railway_keys.py`
2. Update in Railway → Service → Variables
3. Redeploy

### API Key:
1. Generate new key
2. Update in Railway
3. Update local `config.ini`
4. Redeploy

### Admin Password:
1. Login to web app
2. (Feature to change password will be in user settings)
3. Or regenerate via Railway console

## 📝 GitGuardian Alerts

If GitGuardian alerts on this repo:
- ✅ **Ignore** alerts for `generate_railway_keys.py` - it's a generator script
- ✅ **Ignore** alerts for example files and documentation
- ⚠️ **Investigate** any alerts for actual config files

The keys shown in the generator script output are **examples** generated for demonstration. Real production keys are different and only in Railway.

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability:
1. **DO NOT** open a public issue
2. Contact the repository owner privately
3. Allow time for fix before disclosure

## ✅ Best Practices

- ✅ Use environment variables for all secrets
- ✅ Rotate keys regularly (every 3-6 months)
- ✅ Use strong passwords (16+ characters)
- ✅ Enable 2FA where available
- ✅ Review Railway access logs periodically
- ✅ Never commit `.env` or `config.ini`

## 📚 Resources

- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

