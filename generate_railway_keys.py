"""
Generate secure keys for Railway deployment

This script generates NEW random keys each time you run it.
Never commit the actual keys to git - only use this script to generate them.
"""
import secrets

print("="*60)
print(" Railway Environment Variables Generator")
print("="*60)
print("\nRun this script to generate NEW secure keys:")
print("python generate_railway_keys.py\n")
print("="*60)

print("\n# Security Keys (IMPORTANT - keep these secret!)")
# Note: These keys are generated FRESH each time you run this script
# They are NOT actual production secrets - just examples of format
# ggignore: This is a key generator, not actual secrets
print(f"SECRET_KEY={secrets.token_urlsafe(32)}")
print(f"API_KEY={secrets.token_urlsafe(32)}")

print("\n# Admin User (change password after first login)")
print("ADMIN_USERNAME=admin")
print("ADMIN_PASSWORD=ChangeThisPassword123!")
print("ADMIN_EMAIL=admin@company.com")

print("\n# Flask Configuration")
print("FLASK_ENV=production")
print("PORT=5000")

print("\n# Database (Railway sets this automatically)")
print("DATABASE_URL=${{Postgres.DATABASE_URL}}")

print("\n" + "="*60)
print(" Instructions:")
print("="*60)
print("1. Copy ALL variables above")
print("2. Go to Railway → Your Service → Variables tab")
print("3. Add each variable (one by one or use 'RAW Editor')")
print("4. Click 'Add' or 'Save'")
print("5. Railway will auto-redeploy")
print("="*60)

