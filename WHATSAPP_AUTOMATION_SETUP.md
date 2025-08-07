# 🆓 FREE WHATSAPP AUTOMATION SETUP

## IFTTT Setup (5 minutes):

1. Go to: https://ifttt.com/join
2. Create free account
3. Go to: https://ifttt.com/maker_webhooks
4. Click "Connect"
5. Go to: https://ifttt.com/maker_webhooks/settings
6. Copy your webhook key

## Create Applet:

1. Go to: https://ifttt.com/create
2. Click "If This" → Search "Webhooks" → "Receive a web request"
3. Event Name: "new_job_alert"
4. Click "Then That" → Search "WhatsApp" → "Send message to WhatsApp group"
5. Message: "{{Value1}}"
6. Choose your WhatsApp group
7. Save applet

## Update Your App:

1. Copy webhook URL: https://maker.ifttt.com/trigger/new_job_alert/with/key/YOUR_KEY
2. Replace YOUR_KEY with actual key from step 6
3. Set in Heroku: Config Vars → WHATSAPP_WEBHOOK_URL

## Test:

Visit: http://localhost:5000/test-whatsapp

## How it works:

- Your app finds new job → Sends to IFTTT → IFTTT sends to WhatsApp group
- Completely automatic!
- Zero manual work!
- 100% FREE!

## Limitations (Free Plan):

- 100 automations/month (more than enough for jobs)
- Single WhatsApp group
- Basic message format

## Backup Option:

If IFTTT fails, messages are still saved in whatsapp_messages.json for manual sending.
