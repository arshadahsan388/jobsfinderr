# 🔥 HEROKU DEPLOYMENT GUIDE

## 🚀 Method 1: GitHub Integration (Recommended)

### Step-by-step process:

#### 1. Account Verification

- Go to: https://heroku.com/verify
- Add payment method (free tier still available)
- Verify your account

#### 2. Create New App

- Go to: https://dashboard.heroku.com/new-app
- App name: `flask-jobsite-ahsan` (or any unique name)
- Region: United States
- Click "Create app"

#### 3. Connect GitHub

- In app dashboard, go to "Deploy" tab
- Select "GitHub" as deployment method
- Connect GitHub account
- Search for repository: `jobsfinderr`
- Click "Connect"

#### 4. Enable Automatic Deploys

- Scroll down to "Automatic deploys"
- Select branch: `master`
- Click "Enable Automatic Deploys"

#### 5. Manual Deploy (First Time)

- Scroll to "Manual deploy"
- Select branch: `master`
- Click "Deploy Branch"

## 🛠️ Method 2: Heroku CLI (After Verification)

```bash
# After account verification
heroku create flask-jobsite-ahsan
git push heroku master
heroku open
```

## ✅ Files Ready:

- ✅ Procfile (web: gunicorn app:app)
- ✅ requirements.txt (with all dependencies)
- ✅ runtime.txt (python-3.11.9)
- ✅ Production configuration in app.py

## 🎯 Expected Result:

Your Flask job site will be live at:
`https://flask-jobsite-ahsan.herokuapp.com`

## 🔧 Post-Deployment:

- Scheduler will run every 6 hours
- Jobs will be scraped automatically
- All features will work perfectly

## 📝 Important Notes:

- Heroku free tier has limited hours (dyno hours)
- App may sleep after 30 minutes of inactivity
- For production, consider upgrading to paid plan
