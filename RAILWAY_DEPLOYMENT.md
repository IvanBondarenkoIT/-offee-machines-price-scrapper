# Railway Deployment Guide

Complete guide to deploy the Coffee Price Monitor web application on Railway.com

## Prerequisites

- Railway.com account (free tier available)
- GitHub repository (this project)
- Basic understanding of environment variables

## Step 1: Database Setup

### Create PostgreSQL Database

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Provision PostgreSQL"
4. Wait for database to be created
5. Go to "Variables" tab
6. Copy `DATABASE_URL` value

## Step 2: Web Application Setup

### Deploy from GitHub

1. In the same project, click "New Service"
2. Select "GitHub Repo"
3. Choose your repository
4. Railway will auto-detect `Dockerfile`
5. Wait for initial deployment (will fail - need env vars)

### Configure Environment Variables

Go to your web service → "Variables" tab and add:

```env
# Required
SECRET_KEY=your-secret-key-here-generate-random-string
DATABASE_URL=${{Postgres.DATABASE_URL}}
API_KEY=your-api-key-here-generate-random-string

# Admin user
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password

# Flask config
FLASK_ENV=production
PORT=5000
```

**Generate secure keys:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Redeploy

1. Go to "Deployments" tab
2. Click "Deploy" on the latest deployment
3. Wait for build and deploy (3-5 minutes)

## Step 3: Database Initialization

### Run Migrations

1. Open Railway service console (top-right menu → "Console")
2. Run migrations:
```bash
flask db upgrade
```

### Create First Admin User

**Option A: Using Python Console in Railway**
```bash
python
```
```python
from web_app.app import create_app
from web_app.database import db
from web_app.models import User
import os

app = create_app('production')
with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username=os.environ.get('ADMIN_USERNAME', 'admin'),
            email='admin@company.com',
            role='admin'
        )
        admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    else:
        print("Admin user already exists")
```

**Option B: Create init script** (recommended for production)

Create `init_db.py`:
```python
from web_app.app import create_app
from web_app.database import db
from web_app.models import User
import os

def init_admin_user():
    app = create_app('production')
    with app.app_context():
        db.create_all()
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username=os.environ.get('ADMIN_USERNAME', 'admin'),
                email='admin@company.com',
                role='admin'
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD'))
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created successfully")
        else:
            print("✓ Admin user already exists")

if __name__ == '__main__':
    init_admin_user()
```

Run in Railway console:
```bash
python init_db.py
```

## Step 4: Configure Local Uploader

### Get Railway URL

1. Go to your web service
2. Go to "Settings" tab
3. Under "Domains", copy your Railway URL (e.g., `https://your-app.railway.app`)

### Setup Uploader

1. Copy config template:
```bash
copy web_uploader\config.example.ini web_uploader\config.ini
```

2. Edit `web_uploader/config.ini`:
```ini
[API]
url = https://your-app.railway.app/api/upload
key = your-api-key-from-railway

[LOCAL]
data_directory = data/output/excel
```

3. Test upload:
```bash
python web_uploader/uploader.py
```

## Step 5: Verification

### Test Web Application

1. **Open Railway URL**
   - Visit `https://your-app.railway.app`
   - Should see login page

2. **Login**
   - Username: `admin` (or your ADMIN_USERNAME)
   - Password: Your ADMIN_PASSWORD
   - Should redirect to dashboard

3. **Test API**
   ```bash
   curl https://your-app.railway.app/api/health
   ```
   Should return: `{"status": "ok", "service": "Coffee Price Monitor API"}`

### Test Data Upload

1. **Run full cycle locally:**
   ```bash
   python run_full_cycle.py
   ```

2. **Upload to Railway:**
   ```bash
   python web_uploader/uploader.py
   ```

3. **Check web app:**
   - Refresh dashboard
   - Should see uploaded data
   - Check comparison table

## Troubleshooting

### Build Fails

**Error: "Dockerfile not found"**
- Ensure `Dockerfile` is in repository root
- Check Railway is looking at correct branch

**Error: "pip install failed"**
- Check `requirements-web.txt` syntax
- Verify all packages are available on PyPI

### Deploy Fails

**Error: "Application failed to start"**
- Check Railway logs ("Deployments" → "View Logs")
- Verify environment variables are set
- Check DATABASE_URL is correct

**Error: "Port binding failed"**
- Ensure `PORT` env var is set to `5000`
- Check Dockerfile `EXPOSE 5000`

### Database Issues

**Error: "relation does not exist"**
- Run migrations: `flask db upgrade`
- Or manually: `python init_db.py`

**Error: "connection refused"**
- Check DATABASE_URL format
- Verify PostgreSQL service is running
- Check both services are in same project

### Upload Issues

**Error: "Authentication failed"**
- Verify API_KEY in Railway matches config.ini
- Check `X-API-Key` header is being sent

**Error: "Connection refused"**
- Verify Railway URL is correct
- Check web service is deployed
- Test with `curl` first

## Monitoring

### View Logs

Railway Dashboard → Your Service → "Deployments" → "View Logs"

### Check Database

Railway Dashboard → PostgreSQL → "Data" tab

### Metrics

Railway provides:
- CPU usage
- Memory usage
- Request counts
- Response times

## Maintenance

### Update Application

1. Push code to GitHub
2. Railway auto-deploys (if enabled)
3. Or manually trigger deploy in Railway

### Database Backup

1. Railway Dashboard → PostgreSQL
2. "Backups" tab
3. "Create Backup"
4. Download if needed

### Rotate API Key

1. Generate new key:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. Update Railway env var `API_KEY`
3. Update local `config.ini`
4. Redeploy if needed

## Cost Estimation

### Railway Free Tier
- $5 credit per month
- Enough for:
  - Web service (1 replica)
  - PostgreSQL database
  - ~500-1000 requests/day

### Paid Plan (if needed)
- $5/month minimum
- Pay-as-you-go for resources
- Typically $10-20/month for this app

## Security Checklist

- [ ] Strong SECRET_KEY (32+ characters)
- [ ] Strong API_KEY (32+ characters)
- [ ] Strong ADMIN_PASSWORD
- [ ] DATABASE_URL kept secret
- [ ] HTTPS enabled (automatic on Railway)
- [ ] config.ini NOT committed to git
- [ ] .env files NOT committed to git

## Support

### Railway Support
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

### Project Support
- GitHub Issues
- Check logs first
- Include error messages

## Next Steps

1. ✅ Deploy database
2. ✅ Deploy web app
3. ✅ Configure env vars
4. ✅ Run migrations
5. ✅ Create admin user
6. ✅ Test login
7. ✅ Setup uploader
8. ✅ Upload first data
9. ✅ Verify everything works
10. 🎉 Share with team!

---

**Congratulations!** Your Coffee Price Monitor is now live! 🚀☕

