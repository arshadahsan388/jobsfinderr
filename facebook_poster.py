# Facebook Page Auto Poster Integration
# This will automatically post jobs to your Facebook page when new jobs are found

import requests
import json
import os
from datetime import datetime
import urllib.parse

class FacebookPoster:
    def __init__(self):
        # Facebook Page Access Token - Get from Facebook Developers
        self.page_access_token = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', 'YOUR_PAGE_ACCESS_TOKEN_HERE')
        self.page_id = os.environ.get('FACEBOOK_PAGE_ID', 'YOUR_PAGE_ID_HERE')
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def post_to_page(self, message, link=None):
        """Post message to Facebook page"""
        try:
            url = f"{self.base_url}/{self.page_id}/feed"
            
            payload = {
                'message': message,
                'access_token': self.page_access_token
            }
            
            # Add link if provided
            if link:
                payload['link'] = link
            
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'id' in result:
                    print(f"✅ Facebook post created successfully: {result['id']}")
                    return True
                else:
                    print(f"❌ Facebook API error: {result}")
                    return False
            else:
                print(f"❌ Facebook request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Facebook posting error: {e}")
            return False
    
    def format_job_for_facebook(self, job):
        """Format job data for Facebook post"""
        
        # Create emoji based on job type
        job_type = job.get('details', {}).get('Job Type', 'Private')
        emoji = "🏛️" if job_type.lower() == 'government' else "🏢"
        
        # Format message for Facebook
        message = f"""🔥 NEW JOB ALERT {emoji}

{job.get('title', 'N/A')}

📍 Location: {job.get('details', {}).get('Location', 'Not specified')}
👥 Vacancies: {job.get('details', {}).get('Total Vacancies', 'Not specified')}
🎓 Education: {job.get('details', {}).get('Education', 'Not specified')}
💰 Salary: {job.get('details', {}).get('Salary', 'Not specified')}
📅 Last Date: {job.get('details', {}).get('Last Date for Apply', 'Not specified')}
⚡ Job Type: {job_type}

🔗 Apply Now: https://jobsfinderr.me/job/{job.get('id')}

Share this opportunity with your friends! 👥

#JobAlert #PakistanJobs #{job_type}Jobs #JobsFindeRR #Career #Employment #JobOpportunity #Hiring"""
        
        return message
    
    def test_connection(self):
        """Test Facebook API connection"""
        try:
            url = f"{self.base_url}/{self.page_id}"
            params = {
                'fields': 'name,id',
                'access_token': self.page_access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                page_info = response.json()
                print(f"✅ Connected to Facebook Page: {page_info.get('name')} (ID: {page_info.get('id')})")
                return True
            else:
                print(f"❌ Facebook connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Facebook connection error: {e}")
            return False

def send_facebook_job_notification(job):
    """Send job notification to Facebook page"""
    facebook = FacebookPoster()
    
    # Test connection first
    if not facebook.test_connection():
        print("❌ Facebook connection failed - skipping post")
        return False
    
    # Format message
    message = facebook.format_job_for_facebook(job)
    job_link = f"https://jobsfinderr.me/job/{job.get('id')}"
    
    # Post to Facebook
    success = facebook.post_to_page(message, job_link)
    
    if success:
        print(f"🚀 Facebook post created for: {job.get('title')}")
    else:
        print(f"❌ Failed to create Facebook post for: {job.get('title')}")
    
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
    
    print("Testing Facebook Poster...")
    send_facebook_job_notification(sample_job)
