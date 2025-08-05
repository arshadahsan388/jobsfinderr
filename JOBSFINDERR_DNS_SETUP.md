# 🎯 DNS Setup for jobsfinderr.me (Namecheap)

## ✅ COMPLETED: Domain Added to Heroku

- ✅ jobsfinderr.me
- ✅ www.jobsfinderr.me

## 🔧 DNS Configuration Required:

### Login to Namecheap:

1. Go to: https://www.namecheap.com/myaccount/login/
2. Login with your credentials
3. Go to "Domain List"
4. Click "Manage" next to jobsfinderr.me
5. Click "Advanced DNS" tab

### Add These DNS Records:

**Record 1 - WWW Subdomain:**

```
Type: CNAME Record
Host: www
Value: opaque-wildcat-ngfl9juu2wrlulpgbt1537g0.herokudns.com
TTL: Automatic
```

**Record 2 - Root Domain (Use URL Redirect since ALIAS not available):**

```
Type: URL Redirect Record
Host: @
Value: https://www.jobsfinderr.me
Redirect Type: 301 - Permanent Redirect
```

**Alternative Record 2 (If URL Redirect not working, use A Record):**
First get Heroku IP by running: `nslookup colorful-reaches-qn5cjcod0e0ka4hda2b5irp9.herokudns.com`

```
Type: A Record
Host: @
Value: [IP address from nslookup]
TTL: Automatic
```

### Remove Default Records:

- Delete any existing A records for @ and www
- Delete any existing CNAME records for www

## ⏱️ Timeline:

- **Setup time**: 2-5 minutes
- **DNS Propagation**: 2-24 hours (usually 2-4 hours)
- **SSL Certificate**: Automatic (within 1 hour after DNS propagation)

## 🧪 Testing:

After DNS propagation, test these URLs:

- ✅ https://jobsfinderr.me
- ✅ https://www.jobsfinderr.me

## 📞 Support:

If any issues, check:

- Namecheap DNS Manager
- `nslookup jobsfinderr.me`
- `nslookup www.jobsfinderr.me`

## 🎉 Final Result:

Your Flask job site will be live at:
**https://jobsfinderr.me** and **https://www.jobsfinderr.me**
