# Facebook Page Auto Posting Setup Guide

Ye guide aapko batayega ke kaise aap apne Facebook page pe automatic job posting setup kar sakte hain.

## Step 1: Facebook Developer Account Setup

1. **Facebook Developers** pe jaayen: https://developers.facebook.com/
2. **"My Apps"** pe click karein
3. **"Create App"** pe click karein
4. **"Business"** select karein aur Next pe click karein
5. App ka naam enter karein (jaise "JobsFindeRR Auto Poster")
6. App create kar dein

## Step 2: Facebook Page Access Token Generate Karein

1. Apni Facebook app mein jaayen
2. Left sidebar mein **"Add Product"** pe click karein
3. **"Facebook Login"** add karein
4. **Graph API Explorer** open karein: https://developers.facebook.com/tools/explorer/
5. **"Get Token"** dropdown mein se **"Get Page Access Token"** select karein
6. Apna page select karein
7. Required permissions select karein:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`
8. **"Generate Access Token"** pe click karein
9. Token ko copy kar lein (ye long-lived token hai)

## Step 3: Page ID Find Karein

### Method 1: Facebook Page Settings

1. Apne Facebook page pe jaayen
2. **"Settings"** pe click karein
3. Left sidebar mein **"Page Info"** pe click karein
4. **"Page ID"** copy kar lein

### Method 2: Graph API Explorer

1. Graph API Explorer mein jaayen
2. GET request karein: `me/accounts`
3. Apne page ka ID find kar lein

## Step 4: Environment Variables Set Karein

### Heroku Deployment ke liye:

```bash
heroku config:set FACEBOOK_PAGE_ACCESS_TOKEN="your_page_access_token_here"
heroku config:set FACEBOOK_PAGE_ID="your_page_id_here"
```

### Local Development ke liye:

`.env` file banayein aur ye add karein:

```
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here
```

## Step 5: Test Karna

1. **Local Testing:**

   ```bash
   python facebook_poster.py
   ```

2. **Web Testing:**
   - Browser mein jaayen: `http://localhost:5000/test-facebook`
   - Ya production mein: `https://jobsfinderr.me/test-facebook`

## Step 6: Facebook App Review (Optional)

Agar aap public use ke liye app banani hai to:

1. Facebook App Review submit karein
2. Required permissions ke liye approval lein
3. Privacy Policy aur Terms of Service provide karein

## Important Notes:

### Security:

- **Never commit tokens to GitHub**
- Use environment variables only
- Regularly rotate access tokens

### Rate Limits:

- Facebook has API rate limits
- Don't post too frequently
- Current setup posts only when new jobs are found

### Token Expiry:

- Page Access Tokens can expire
- Monitor logs for authentication errors
- Regenerate tokens if needed

## Troubleshooting:

### Error: "Invalid access token"

- Check if token is correct
- Verify environment variables are set
- Regenerate token if expired

### Error: "Insufficient permissions"

- Add required permissions to your app
- Get approval for `pages_manage_posts`

### Error: "Page not found"

- Verify Page ID is correct
- Check if you have admin access to the page

## Testing Commands:

### Test Facebook Connection:

```python
from facebook_poster import FacebookPoster
fb = FacebookPoster()
fb.test_connection()
```

### Test Job Posting:

```python
from facebook_poster import send_facebook_job_notification
# Sample job data...
send_facebook_job_notification(sample_job)
```

## Support:

Agar koi problem hai to:

1. Logs check karein
2. Facebook Developer Console mein errors dekhen
3. Environment variables verify karein

## Features:

✅ **Automatic posting** when new jobs are found
✅ **Rich formatting** with emojis and hashtags
✅ **Job links** included in posts
✅ **Error handling** with detailed logs
✅ **Test endpoints** for debugging
✅ **Both Telegram and Facebook** posting together

---

**Note:** Ye system completely automatic hai. Jab bhi new jobs milenge, wo Telegram aur Facebook dono pe post ho jaayengi!
