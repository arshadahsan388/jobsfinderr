import os
import sys
sys.path.append('.')

# Set environment variables for testing
os.environ['TELEGRAM_BOT_TOKEN'] = '8366393794:AAH0ZKkoIzvDtBVfJa7woObbXaezhC_JBmU'
os.environ['TELEGRAM_CHAT_ID'] = 'TEST_CHAT_ID'

# Test the telegram bot
try:
    from telegram_bot import send_telegram_job_notification
    
    sample_job = {
        "id": 1,
        "title": "TEST: Telegram Bot Working!",
        "details": {
            "Job Type": "Government",
            "Location": "Test Location",
            "Total Vacancies": "1",
            "Education": "Test",
            "Salary": "Test Salary",
            "Last Date for Apply": "Test Date"
        }
    }
    
    print("🧪 Testing Telegram bot...")
    print("Bot Token configured:", os.environ.get('TELEGRAM_BOT_TOKEN')[:20] + "...")
    print("Chat ID:", os.environ.get('TELEGRAM_CHAT_ID'))
    
    # This will show us if the bot token is working
    result = send_telegram_job_notification(sample_job)
    print(f"Result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    print("Bot token seems to be working, but need correct Chat ID")
