import requests
import json
from datetime import datetime
import os

class WhatsAppAutomation:
    def __init__(self):
        # You'll need to get these from WhatsApp Business API or use a service like Twilio
        self.api_url = "https://api.whatsapp.com/send"  # This is for manual links
        self.group_id = ""  # WhatsApp Group Chat ID
        self.api_token = ""  # API Token for WhatsApp Business
        
    def format_job_message(self, job):
        """Format job data into WhatsApp message"""
        
        # Create emoji based on job type
        job_type = job.get('details', {}).get('Job Type', 'Private')
        emoji = "🏛️" if job_type.lower() == 'government' else "🏢"
        
        # Format the message
        message = f"""🔥 *NEW JOB ALERT* {emoji}
        
*{job.get('title', 'N/A')}*

📍 *Location:* {job.get('details', {}).get('Location', 'Not specified')}
👥 *Vacancies:* {job.get('details', {}).get('Total Vacancies', 'Not specified')}
🎓 *Education:* {job.get('details', {}).get('Education', 'Not specified')}
💰 *Salary:* {job.get('details', {}).get('Salary', 'Not specified')}
📅 *Last Date:* {job.get('details', {}).get('Last Date for Apply', 'Not specified')}
⚡ *Job Type:* {job_type}

Apply here: https://jobsfinderr.me/job/{job.get('id')}

#JobAlert #PakistanJobs #{job_type}Jobs"""
        
        return message
    
    def create_whatsapp_link(self, message, phone_number=None):
        """Create WhatsApp share link"""
        import urllib.parse
        
        encoded_message = urllib.parse.quote(message)
        
        if phone_number:
            # Send to specific number
            return f"https://wa.me/{phone_number}?text={encoded_message}"
        else:
            # General WhatsApp share
            return f"https://wa.me/?text={encoded_message}"
    
    def send_to_webhook(self, message):
        """Send message via webhook (IFTTT, Zapier, etc.)"""
        try:
            webhook_url = os.environ.get('WHATSAPP_WEBHOOK_URL')
            if not webhook_url:
                print("❌ No webhook URL configured")
                return False
            
            # IFTTT format
            if 'maker.ifttt.com' in webhook_url:
                payload = {
                    "value1": message,  # IFTTT uses value1, value2, value3
                    "value2": "JobsFinderr",
                    "value3": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                # General webhook format
                payload = {
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "source": "JobsFinderr"
                }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print("✅ Message sent to WhatsApp webhook successfully")
                return True
            else:
                print(f"❌ Webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ WhatsApp webhook error: {e}")
            return False
    
    def save_message_for_manual_send(self, message, job_id):
        """Save message to file for manual sending"""
        try:
            messages_file = "whatsapp_messages.json"
            
            # Load existing messages
            if os.path.exists(messages_file):
                with open(messages_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            else:
                messages = []
            
            # Add new message
            message_data = {
                "id": job_id,
                "message": message,
                "whatsapp_link": self.create_whatsapp_link(message),
                "created_at": datetime.now().isoformat(),
                "sent": False
            }
            
            messages.append(message_data)
            
            # Save updated messages
            with open(messages_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            print(f"✅ WhatsApp message saved for Job ID: {job_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving WhatsApp message: {e}")
            return False

def send_new_job_notification(job):
    """Send WhatsApp notification for new job"""
    whatsapp = WhatsAppAutomation()
    
    # Format message
    message = whatsapp.format_job_message(job)
    
    # Try webhook first (for automation)
    webhook_success = whatsapp.send_to_webhook(message)
    
    # Always save for manual sending
    manual_save = whatsapp.save_message_for_manual_send(message, job.get('id'))
    
    if webhook_success:
        print(f"🚀 Auto-sent WhatsApp notification for: {job.get('title')}")
    elif manual_save:
        print(f"📱 WhatsApp message ready for manual send: {job.get('title')}")
        print(f"🔗 Link: {whatsapp.create_whatsapp_link(message)}")
    
    return webhook_success or manual_save

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
    
    send_new_job_notification(sample_job)
