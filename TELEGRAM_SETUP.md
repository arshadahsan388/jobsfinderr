# 🤖 TELEGRAM BOT SETUP GUIDE (100% FREE)

## Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram and search for `@BotFather`
2. Send: `/newbot`
3. Bot name: `JobsFinderr Alert Bot`
4. Username: `jobsfinderr_alert_bot` (or any unique name)
5. **Copy the Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrSTUvwxyz`)

## Step 2: Create Channel/Group (1 minute)

1. Create a new Telegram channel or group
2. Add your bot as admin
3. Send a test message mentioning the bot: `@jobsfinderr_alert_bot hello`

## Step 3: Get Chat ID (1 minute)

1. Go to: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
2. Replace `YOUR_BOT_TOKEN` with actual token
3. Look for "chat":{"id": and copy the number (like: -1001234567890)

## Step 4: Set Environment Variables

### Local Testing:

```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz
TELEGRAM_CHAT_ID=-1001234567890
```

### Heroku Deployment:

1. Go to Heroku Dashboard → Your App → Settings
2. Click "Reveal Config Vars"
3. Add:
   - Key: `TELEGRAM_BOT_TOKEN`, Value: `your_bot_token`
   - Key: `TELEGRAM_CHAT_ID`, Value: `your_chat_id`

## Step 5: Test the System

### Local Test:

```bash
python telegram_bot.py
```

### Web Test:

```
http://localhost:5000/test-telegram
```

## How It Works:

1. **Automatic Job Detection:** Your app finds new jobs every 6 hours
2. **Telegram Notification:** Automatically sends to your Telegram channel
3. **WhatsApp Integration:** Each Telegram message includes a "Share to WhatsApp" link
4. **Manual Forward:** Click the WhatsApp link to share in WhatsApp groups
5. **Zero Cost:** Completely free, unlimited messages

## Message Format:

```
🔥 NEW JOB ALERT 🏛️

Health Department Balochistan Jobs 2025

📍 Location: Balochistan, Quetta
👥 Vacancies: 103
🎓 Education: Graduation, Master Degree
💰 Salary: PKR 40000 – 150000
📅 Last Date: 06 August 2025
⚡ Job Type: Government

🔗 Apply Here: [Link]

🚀 Share this job:
📱 WhatsApp: [Click to Share]
📋 Copy & Paste for WhatsApp Groups

#JobAlert #PakistanJobs #GovernmentJobs
```

## Benefits:

✅ **100% Free** - No monthly charges
✅ **Automatic** - Zero manual work for Telegram
✅ **WhatsApp Ready** - One-click sharing to WhatsApp
✅ **Professional** - Clean, formatted messages
✅ **Unlimited** - No message limits
✅ **Fast Setup** - 5 minutes total

## Troubleshooting:

- **Bot not responding:** Check if bot is admin in channel
- **Messages not sending:** Verify bot token and chat ID
- **Permission errors:** Ensure bot has send message permissions

## Next Steps:

1. Complete bot setup (5 minutes)
2. Test locally
3. Deploy to Heroku with environment variables
4. Enjoy automatic job alerts!

The system will automatically:

- Detect new jobs → Send to Telegram → Provide WhatsApp sharing links
- Work 24/7 without any manual intervention
- Handle unlimited job alerts for free!
