# Discord Webhook Integration (FREE Alternative)

import requests
import json
from datetime import datetime

def send_to_discord_webhook(message, job_title):
    """Send job alert to Discord channel (FREE)"""
    try:
        # Discord webhook URL (you'll get this from Discord server settings)
        webhook_url = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
        
        # Format for Discord
        discord_payload = {
            "content": f"🔥 **NEW JOB ALERT** 🔥",
            "embeds": [{
                "title": job_title,
                "description": message,
                "color": 3447003,  # Blue color
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "JobsFinderr - Pakistan Jobs Portal"
                }
            }]
        }
        
        response = requests.post(webhook_url, json=discord_payload)
        
        if response.status_code == 204:
            print("✅ Discord notification sent successfully")
            return True
        else:
            print(f"❌ Discord webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Discord webhook error: {e}")
        return False

# Example usage
if __name__ == "__main__":
    test_message = """
🔥 *NEW JOB ALERT* 🏛️

*Health Department Balochistan Jobs 2025*

📍 *Location:* Balochistan, Quetta
👥 *Vacancies:* 103
🎓 *Education:* Graduation, Master Degree
💰 *Salary:* PKR 40000 – 150000
📅 *Last Date:* 06 August 2025
⚡ *Job Type:* Government

Apply here: https://jobsfinderr-app.herokuapp.com/job/1

#JobAlert #PakistanJobs #GovernmentJobs
    """
    
    send_to_discord_webhook(test_message, "Health Department Jobs 2025")
