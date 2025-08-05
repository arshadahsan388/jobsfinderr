# 🌐 Custom Domain Setup Guide for Heroku

## Prerequisites:

- ✅ Heroku app deployed (DONE: flask-jobsite-app-2025)
- 🔍 Need: Custom domain name (e.g., yoursite.com)

## Step 1: Buy Domain (if not already owned)

**Recommended providers:**

- **Namecheap**: https://www.namecheap.com/ (affordable)
- **GoDaddy**: https://www.godaddy.com/ (popular)
- **Google Domains**: https://domains.google/
- **Cloudflare**: https://www.cloudflare.com/products/registrar/

## Step 2: Add Domain to Heroku

### Using Heroku CLI:

```bash
# Add your domain (replace 'yourdomain.com' with actual domain)
heroku domains:add yourdomain.com --app flask-jobsite-app-2025
heroku domains:add www.yourdomain.com --app flask-jobsite-app-2025

# Get DNS settings
heroku domains --app flask-jobsite-app-2025
```

### Using Heroku Dashboard:

1. Go to: https://dashboard.heroku.com/apps/flask-jobsite-app-2025
2. Click "Settings" tab
3. Scroll to "Domains" section
4. Click "Add domain"
5. Enter your domain name
6. Copy the DNS target provided

## Step 3: Configure DNS at Domain Provider

### For Namecheap:

1. Login to Namecheap
2. Manage Domain → Advanced DNS
3. Add these records:

```
Type: CNAME
Host: www
Value: [heroku-dns-target]
TTL: Automatic

Type: ALIAS or ANAME (if available)
Host: @
Value: [heroku-dns-target]
TTL: Automatic
```

### For GoDaddy:

1. Login to GoDaddy
2. DNS Management
3. Add records:

```
Type: CNAME
Name: www
Value: [heroku-dns-target]

Type: Forwarding (for root domain)
Forward to: https://www.yourdomain.com
```

## Step 4: SSL Certificate (Automatic)

Heroku automatically provides SSL certificates for custom domains.

## Step 5: Verification

- DNS propagation: 24-48 hours (usually 2-4 hours)
- Check: `nslookup yourdomain.com`
- Test: `https://yourdomain.com`

## 🎯 Example Commands (Replace 'example.com' with your domain):

```bash
# Add domain
heroku domains:add example.com --app flask-jobsite-app-2025
heroku domains:add www.example.com --app flask-jobsite-app-2025

# Check status
heroku domains --app flask-jobsite-app-2025

# Check SSL
heroku certs --app flask-jobsite-app-2025
```

## ⚠️ Important Notes:

- Use www subdomain for better compatibility
- Root domain forwarding to www is recommended
- SSL certificate is free and automatic
- DNS changes take time to propagate

## 🔗 After Setup:

Your job site will be accessible at:

- https://yourdomain.com
- https://www.yourdomain.com
- Original Heroku URL still works as backup
