import requests
import json
from datetime import datetime

class IndexNowSubmitter:
    """
    IndexNow API implementation for instant search engine indexing
    Supports Google, Bing, and other search engines
    """
    
    def __init__(self):
        self.base_url = "https://api.indexnow.org/indexnow"
        self.key = "jobsfinderr-indexnow-2025"  # Your unique key
        self.host = "jobsfinderr.me"
        
    def submit_urls(self, urls):
        """Submit URLs for immediate indexing"""
        payload = {
            "host": self.host,
            "key": self.key,
            "urlList": urls
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.base_url, 
                data=json.dumps(payload), 
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully submitted {len(urls)} URLs for indexing")
                return True
            else:
                print(f"❌ IndexNow submission failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ IndexNow error: {e}")
            return False
    
    def submit_new_job(self, job_url):
        """Submit a single new job URL"""
        return self.submit_urls([job_url])
    
    def submit_priority_pages(self):
        """Submit all priority pages for indexing"""
        priority_urls = [
            "https://jobsfinderr.me/",
            "https://jobsfinderr.me/government-jobs",
            "https://jobsfinderr.me/private-jobs",
            "https://jobsfinderr.me/jobs/karachi",
            "https://jobsfinderr.me/jobs/lahore", 
            "https://jobsfinderr.me/jobs/islamabad",
            "https://jobsfinderr.me/jobs/peshawar",
            "https://jobsfinderr.me/jobs/quetta",
            "https://jobsfinderr.me/about",
            "https://jobsfinderr.me/contact"
        ]
        
        return self.submit_urls(priority_urls)

def quick_index_submission():
    """Quick function to submit priority pages for indexing"""
    indexer = IndexNowSubmitter()
    
    print("🚀 Submitting website for instant indexing...")
    success = indexer.submit_priority_pages()
    
    if success:
        print("✅ Priority pages submitted to search engines!")
        print("📊 This should speed up indexing significantly")
    else:
        print("❌ Submission failed - will try again later")
    
    return success

if __name__ == "__main__":
    # Test the IndexNow submission
    quick_index_submission()
