# Telegram Bot Integration (100% FREE)

import requests
import json
import os
from datetime import datetime
from helpers import create_job_slug

class TelegramBot:
    def __init__(self):
        # Get from BotFather
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_HERE')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message):
        """Send message to Telegram channel/group"""
        try:
            url = f"{self.base_url}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, data=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print("✅ Telegram message sent successfully")
                    return True
                else:
                    print(f"❌ Telegram API error: {result.get('description')}")
                    return False
            else:
                print(f"❌ Telegram request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def format_job_for_telegram(self, job):
        """Format job data for Telegram with Markdown"""
        
        # Create emoji based on job type
        job_type = job.get('details', {}).get('Job Type', 'Private')
        emoji = "🏛️" if job_type.lower() == 'government' else "🏢"
        
        # Format message with Markdown
        message = f"""🔥 *NEW JOB ALERT* {emoji}

*{job.get('title', 'N/A')}*

📍 *Location:* {job.get('details', {}).get('Location', 'Not specified')}
👥 *Vacancies:* {job.get('details', {}).get('Total Vacancies', 'Not specified')}
🎓 *Education:* {job.get('details', {}).get('Education', 'Not specified')}
💰 *Salary:* {job.get('details', {}).get('Salary', 'Not specified')}
📅 *Last Date:* {job.get('details', {}).get('Last Date for Apply', 'Not specified')}
⚡ *Job Type:* {job_type}

🔗 [Apply Here](https://jobsfinderr.me/job/{self._get_job_slug(job)})

#JobAlert #PakistanJobs #{job_type}Jobs
        
🚀 *Share this job:*
📱 WhatsApp: [Click to Share](https://wa.me/?text={self._encode_whatsapp_message(job)})
📋 Copy & Paste for WhatsApp Groups"""
        
        return message
    
    def _get_job_slug(self, job):
        """Get job slug for URL"""
        return create_job_slug(job)
    
    def _encode_whatsapp_message(self, job):
        """Create WhatsApp share text"""
        import urllib.parse
        
        job_type = job.get('details', {}).get('Job Type', 'Private')
        emoji = "🏛️" if job_type.lower() == 'government' else "🏢"
        
        whatsapp_text = f"""🔥 *NEW JOB ALERT* {emoji}

*{job.get('title', 'N/A')}*

📍 *Location:* {job.get('details', {}).get('Location', 'Not specified')}
👥 *Vacancies:* {job.get('details', {}).get('Total Vacancies', 'Not specified')}
🎓 *Education:* {job.get('details', {}).get('Education', 'Not specified')}
💰 *Salary:* {job.get('details', {}).get('Salary', 'Not specified')}
📅 *Last Date:* {job.get('details', {}).get('Last Date for Apply', 'Not specified')}
⚡ *Job Type:* {job_type}

Apply here: https://jobsfinderr.me/job/{create_job_slug(job)}

#JobAlert #PakistanJobs #{job_type}Jobs"""
        
        return urllib.parse.quote(whatsapp_text)
    
    def get_chat_id(self):
        """Get chat ID for your channel/group"""
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url)
            
            if response.status_code == 200:
                updates = response.json()
                print("Recent chats:")
                for update in updates.get('result', []):
                    if 'message' in update:
                        chat = update['message']['chat']
                        print(f"Chat ID: {chat['id']}, Type: {chat['type']}, Title: {chat.get('title', chat.get('first_name', 'Unknown'))}")
                return True
            else:
                print("❌ Failed to get updates")
                return False
                
        except Exception as e:
            print(f"❌ Error getting chat ID: {e}")
            return False

def send_telegram_job_notification(job):
    """Send job notification to Telegram"""
    telegram = TelegramBot()
    
    # Format message
    message = telegram.format_job_for_telegram(job)
    
    # Send to Telegram
    success = telegram.send_message(message)
    
    if success:
        print(f"🚀 Telegram notification sent for: {job.get('title')}")
    else:
        print(f"❌ Failed to send Telegram notification for: {job.get('title')}")
    
    return success

# Test function
if __name__ == "__main__":
    # Test with sample job
    sample_job = {
        "id": 1,
        "title": "Health Department Balochistan Jobs 2025",
        "details": {
            "Job Type": "Government",
            "Location": "Balochistan, Quetta",
            "Total Vacancies": "103",
            "Education": "Graduation, Master Degree",
            "Salary": "PKR 40000 – 150000",
            "Last Date for Apply": "06 August 2025"
        }
    }
    
    print("Testing Telegram Bot...")
    send_telegram_job_notification(sample_job)
