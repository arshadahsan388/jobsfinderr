from flask import Flask, render_template, jsonify, abort, url_for, Response, request, redirect
import json
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import schedule
import time
import threading
import subprocess

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__ ,static_folder='static')

# Force HTTPS and handle www redirects
@app.before_request
def force_https():
    """Force HTTPS and handle www subdomain redirects"""
    # Skip redirects for local development
    if request.host.startswith('127.0.0.1') or request.host.startswith('localhost'):
        return
    
    # Force HTTPS
    if not request.is_secure and not request.headers.get('X-Forwarded-Proto') == 'https':
        return redirect(request.url.replace('http://', 'https://'), code=301)
    
    # Handle www redirect - redirect www to non-www
    if request.host.startswith('www.'):
        non_www_url = request.url.replace('www.', '', 1)
        return redirect(non_www_url, code=301)
    
    # Handle jobsfinderr-app.herokuapp.com to jobsfinderr.me redirect
    if 'jobsfinderr-app.herokuapp.com' in request.host:
        new_url = request.url.replace('jobsfinderr-app.herokuapp.com', 'jobsfinderr.me')
        return redirect(new_url, code=301)

@app.after_request
def add_security_headers(response):
    """Add security headers for HTTPS and SEO"""
    # HTTPS Security Headers
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Cache Control for better performance
    if request.endpoint == 'static':
        response.headers['Cache-Control'] = 'public, max-age=86400'  # 1 day for static files
    
    return response

# Initialize scheduler for production
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_scripts, trigger="interval", hours=6)
    scheduler.start()
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

# Load jobs from JSON file
def load_jobs():
    with open("jobs_enhanced.json", "r", encoding="utf-8") as file:
        return json.load(file)

@app.route("/")
def home():
    jobs = load_jobs()

    return render_template("index.html", jobs=jobs)

        
# @app.route("/job/<int:job_id>")
# def job_detail(job_id):
#     jobs = load_jobs()
#     job = next((j for j in jobs if j.get("id") == job_id), None)
#     if not job:
#         abort(404)

#     # Load enhanced summary from jobs_enhanced.json
#     with open("jobs_enhanced.json", "r", encoding="utf-8") as f:
#         enhanced_jobs = json.load(f)
    
#     enhanced_job = next((j for j in enhanced_jobs if j.get("id") == job_id), None)
#     if enhanced_job and "enhanced_summary" in enhanced_job:
#         job["enhanced_summary"] = enhanced_job["enhanced_summary"]

#     return render_template("job_detail.html", job=job)

@app.route("/job/<int:job_id>")
def job_detail(job_id):
    with open("jobs_enhanced.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)

    job = next((j for j in jobs if j.get("id") == job_id), None)
    if not job:
        abort(404)

    return render_template("job_detail.html", job=job)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/debug-scheduler")
def debug_scheduler():
    return f"""
    <h2>Scheduler Status Debug</h2>
    <p>Environment: {'Production (Heroku)' if os.environ.get('DYNO') else 'Development'}</p>
    <p>Current Time: {datetime.now()}</p>
    <p>DYNO Environment: {os.environ.get('DYNO', 'Not Set')}</p>
    <p>Manual Scrape: <a href="/manual-scrape">/manual-scrape</a></p>
    """

@app.route("/manual-scrape")
def manual_scrape():
    try:
        run_scripts()
        return "✅ Manual scraping completed successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

@app.route("/test-telegram")
def test_telegram():
    """Test Telegram bot notification"""
    try:
        from telegram_bot import send_telegram_job_notification
        
        # Get a sample job from current data
        jobs = load_jobs()
        if jobs:
            sample_job = jobs[0]  # Use first job as sample
            success = send_telegram_job_notification(sample_job)
            
            if success:
                return f"""
                <h2>✅ Telegram Test Successful!</h2>
                <p>Test notification sent for: <strong>{sample_job.get('title', 'N/A')}</strong></p>
                <p>Check your Telegram channel/group for the message!</p>
                <p><a href="/">← Back to Jobs</a></p>
                """
            else:
                bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', 'Not configured')
                chat_id = os.environ.get('TELEGRAM_CHAT_ID', 'Not configured')
                return f"""
                <h2>❌ Telegram Test Failed</h2>
                <p>Check configuration:</p>
                <ul>
                    <li><strong>Bot Token:</strong> {bot_token[:10]}... (hidden)</li>
                    <li><strong>Chat ID:</strong> {chat_id}</li>
                </ul>
                <h3>Setup Instructions:</h3>
                <ol>
                    <li>Message <a href="https://t.me/BotFather" target="_blank">@BotFather</a></li>
                    <li>Send: /newbot</li>
                    <li>Follow instructions to get bot token</li>
                    <li>Add bot to your channel/group</li>
                    <li>Set environment variables in Heroku</li>
                </ol>
                <p><a href="/">← Back to Jobs</a></p>
                """
        else:
            return "❌ No jobs available for testing"
            
    except Exception as e:
        return f"❌ Error testing Telegram: {e}"

@app.route("/test-facebook")
def test_facebook():
    """Test Facebook posting functionality"""
    try:
        from facebook_poster import send_facebook_job_notification
        
        # Get a sample job from current data
        jobs = load_jobs()
        if jobs:
            sample_job = jobs[0]  # Use first job as sample
            success = send_facebook_job_notification(sample_job)
            
            if success:
                return f"""
                <h2>✅ Facebook Test Successful!</h2>
                <p>Test post created for: <strong>{sample_job.get('title', 'N/A')}</strong></p>
                <p>Check your Facebook page for the post!</p>
                <p><a href="/">← Back to Jobs</a></p>
                """
            else:
                page_token = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', 'Not configured')
                page_id = os.environ.get('FACEBOOK_PAGE_ID', 'Not configured')
                return f"""
                <h2>❌ Facebook Test Failed</h2>
                <p>Check configuration:</p>
                <ul>
                    <li><strong>Page Access Token:</strong> {page_token[:10] if page_token != 'Not configured' else 'Not configured'}... (hidden)</li>
                    <li><strong>Page ID:</strong> {page_id}</li>
                </ul>
                <h3>Setup Instructions:</h3>
                <ol>
                    <li>Go to <a href="https://developers.facebook.com/" target="_blank">Facebook Developers</a></li>
                    <li>Create an app and get Page Access Token</li>
                    <li>Add page_posts, pages_manage_posts permissions</li>
                    <li>Get your Page ID from Facebook page settings</li>
                    <li>Set environment variables in Heroku</li>
                </ol>
                <p><a href="/">← Back to Jobs</a></p>
                """
        else:
            return "❌ No jobs available for testing"
            
    except Exception as e:
        return f"❌ Error testing Facebook: {e}"

@app.route("/test-analytics")
def test_analytics():
    """Test Google Analytics 4 tracking functionality"""
    return f"""
    <h2>🔬 Google Analytics 4 Test Page</h2>
    <p>Use this page to test your GA4 tracking implementation.</p>
    
    <div style="margin: 20px 0;">
        <h3>Test Events:</h3>
        <button onclick="testJobSearch()" style="margin: 5px; padding: 10px;">Test Job Search</button>
        <button onclick="testJobFilter()" style="margin: 5px; padding: 10px;">Test Job Filter</button>
        <button onclick="testJobView()" style="margin: 5px; padding: 10px;">Test Job View</button>
        <button onclick="testJobApply()" style="margin: 5px; padding: 10px;">Test Job Apply</button>
    </div>
    
    <div style="margin: 20px 0;">
        <h3>Check Results:</h3>
        <ol>
            <li>Open <a href="https://analytics.google.com/" target="_blank">Google Analytics</a></li>
            <li>Go to Reports → Realtime → Events</li>
            <li>Click buttons above and watch events appear</li>
            <li>Events should appear within 30 seconds</li>
        </ol>
    </div>
    
    <div style="margin: 20px 0;">
        <h3>Setup Status:</h3>
        <p id="gaStatus">Checking GA4 status...</p>
    </div>
    
    <script>
        // Test functions
        function testJobSearch() {{
            if (typeof gtag !== 'undefined') {{
                gtag('event', 'search', {{
                    search_term: 'test government jobs',
                    event_category: 'Job Search',
                    event_label: 'Test Search'
                }});
                alert('✅ Search event sent to GA4!');
            }} else {{
                alert('❌ GA4 not loaded!');
            }}
        }}
        
        function testJobFilter() {{
            if (typeof gtag !== 'undefined') {{
                gtag('event', 'filter_jobs', {{
                    filter_type: 'government',
                    event_category: 'Job Filter',
                    event_label: 'Test Filter'
                }});
                alert('✅ Filter event sent to GA4!');
            }} else {{
                alert('❌ GA4 not loaded!');
            }}
        }}
        
        function testJobView() {{
            if (typeof gtag !== 'undefined') {{
                gtag('event', 'view_item', {{
                    item_id: 'test_job_123',
                    item_name: 'Test Government Job',
                    item_category: 'government',
                    event_category: 'Job Engagement'
                }});
                alert('✅ Job view event sent to GA4!');
            }} else {{
                alert('❌ GA4 not loaded!');
            }}
        }}
        
        function testJobApply() {{
            if (typeof gtag !== 'undefined') {{
                gtag('event', 'select_item', {{
                    item_id: 'test_job_123',
                    item_name: 'Test Government Job',
                    item_category: 'government',
                    event_category: 'Job Application'
                }});
                alert('✅ Job apply event sent to GA4!');
            }} else {{
                alert('❌ GA4 not loaded!');
            }}
        }}
        
        // Check GA4 status
        window.addEventListener('load', function() {{
            const statusEl = document.getElementById('gaStatus');
            if (typeof gtag !== 'undefined' && typeof ga !== 'undefined' || typeof gtag !== 'undefined') {{
                statusEl.innerHTML = '✅ GA4 is loaded and ready!';
                statusEl.style.color = 'green';
            }} else {{
                statusEl.innerHTML = '❌ GA4 not detected. Check your Measurement ID in base.html';
                statusEl.style.color = 'red';
            }}
        }});
    </script>
    
    <p><a href="/">← Back to Jobs</a></p>
    """

@app.route("/privacy-policy")
def privacy():
    return render_template("privacy_policy.html")

# SEO-Friendly Category Pages
@app.route("/government-jobs")
def government_jobs():
    jobs = load_jobs()
    gov_jobs = [job for job in jobs if job.get('details', {}).get('Job Type', '').lower() == 'government']
    return render_template("category_jobs.html", 
                         jobs=gov_jobs, 
                         category="Government Jobs", 
                         description="Find latest government job opportunities in Pakistan. Apply for govt positions in federal and provincial departments.",
                         keywords="government jobs pakistan, govt jobs, federal jobs, provincial jobs")

@app.route("/private-jobs")
def private_jobs():
    jobs = load_jobs()
    private_jobs = [job for job in jobs if job.get('details', {}).get('Job Type', '').lower() == 'private']
    return render_template("category_jobs.html", 
                         jobs=private_jobs, 
                         category="Private Sector Jobs", 
                         description="Explore private sector job opportunities in Pakistan. Find positions in multinational companies and private organizations.",
                         keywords="private jobs pakistan, private sector, multinational companies, corporate jobs")

# City-specific job pages for local SEO
@app.route("/jobs/<city>")
def city_jobs(city):
    jobs = load_jobs()
    # Filter jobs that mention the city in location
    city_jobs = [job for job in jobs if city.lower() in job.get('details', {}).get('Location', '').lower()]
    
    city_name = city.title()
    return render_template("city_jobs.html", 
                         jobs=city_jobs, 
                         city=city_name,
                         description=f"Find latest job opportunities in {city_name}, Pakistan. Government and private sector positions available.",
                         keywords=f"{city.lower()} jobs, jobs in {city.lower()}, {city.lower()} employment, {city.lower()} careers")

from flask import send_from_directory
import os

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')



@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []

    ten_days_ago = datetime.now().date().isoformat()

    # Static URLs - force HTTPS and correct domain
    base_url = "https://jobsfinderr.me"
    
    # Homepage - highest priority
    pages.append({
        "loc": f"{base_url}/",
        "lastmod": ten_days_ago,
        "priority": "1.0"
    })
    
    # Important category pages
    pages.append({
        "loc": f"{base_url}/government-jobs",
        "lastmod": ten_days_ago,
        "priority": "0.9"
    })
    pages.append({
        "loc": f"{base_url}/private-jobs",
        "lastmod": ten_days_ago,
        "priority": "0.9"
    })
    
    # City-specific pages for local SEO
    major_cities = ["karachi", "lahore", "islamabad", "rawalpindi", "faisalabad", "multan", "hyderabad", "peshawar", "quetta"]
    for city in major_cities:
        pages.append({
            "loc": f"{base_url}/jobs/{city}",
            "lastmod": ten_days_ago,
            "priority": "0.8"
        })
    
    # Static pages
    pages.append({
        "loc": f"{base_url}/about",
        "lastmod": ten_days_ago,
        "priority": "0.7"
    })
    pages.append({
        "loc": f"{base_url}/contact",
        "lastmod": ten_days_ago,
        "priority": "0.7"
    })
    pages.append({
        "loc": f"{base_url}/privacy-policy",
        "lastmod": ten_days_ago,
        "priority": "0.5"
    })

    # Load all jobs from enhanced JSON file
    jobs = load_jobs()

    for job in jobs:
        # Individual job pages - high priority for fresh content
        pages.append({
            "loc": f"{base_url}/job/{job['id']}",
            "lastmod": ten_days_ago,
            "priority": "0.9"
        })

    # XML generation
    xml = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for page in pages:
        url = ET.SubElement(xml, 'url')
        ET.SubElement(url, 'loc').text = page["loc"]
        ET.SubElement(url, 'lastmod').text = page["lastmod"]
        ET.SubElement(url, 'changefreq').text = "daily" if "job/" in page["loc"] else "weekly"
        ET.SubElement(url, 'priority').text = page.get("priority", "0.8")

    sitemap_xml = ET.tostring(xml, encoding="utf-8", method="xml")
    response = Response(sitemap_xml, mimetype='application/xml')
    response.headers['Cache-Control'] = 'public, max-age=86400'  # Cache for 1 day
    return response

@app.route('/indexnow-key.txt')
def indexnow_key():
    """Serve IndexNow verification key"""
    return app.send_static_file('jobsfinderr-indexnow-2025.txt')

@app.route('/submit-indexnow', methods=['POST', 'GET'])
def submit_indexnow():
    """Manually trigger IndexNow submission for instant indexing"""
    try:
        from indexnow_submit import quick_index_submission
        success = quick_index_submission()
        
        if success:
            return jsonify({
                "status": "success",
                "message": "✅ Pages submitted for instant indexing!",
                "note": "Search engines will be notified immediately"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "❌ IndexNow submission failed"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"❌ Error: {str(e)}"
        }), 500



def run_scripts():
    print("✅ Running scraping tasks at", datetime.now())
    try:
        # Use Python executable from environment for Heroku compatibility
        python_cmd = "python"
        if os.environ.get('DYNO'):  # In Heroku, use python directly
            python_cmd = "python"
        
        # Load old jobs before scraping
        old_jobs = set()
        if os.path.exists("jobs_enhanced.json"):
            with open("jobs_enhanced.json", "r", encoding="utf-8") as f:
                old_data = json.load(f)
                old_jobs = {job.get('id') for job in old_data if job.get('id')}
        
        # Run scraping scripts
        subprocess.run([python_cmd, "jobs_data/scrape_jobs.py"], timeout=300, check=True)
        subprocess.run([python_cmd, "enhance_jobs.py"], timeout=300, check=True)
        
        # Check for new jobs and send notifications
        if os.path.exists("jobs_enhanced.json"):
            with open("jobs_enhanced.json", "r", encoding="utf-8") as f:
                new_data = json.load(f)
                
            new_jobs_count = 0
            for job in new_data:
                job_id = job.get('id')
                if job_id and job_id not in old_jobs:
                    # This is a new job - send notifications to both Telegram and Facebook
                    try:
                        # Telegram notification (automatic)
                        from telegram_bot import send_telegram_job_notification
                        telegram_success = send_telegram_job_notification(job)
                        
                        # Facebook page posting (automatic)
                        from facebook_poster import send_facebook_job_notification
                        facebook_success = send_facebook_job_notification(job)
                        
                        new_jobs_count += 1
                        
                        # Log results for both platforms
                        if telegram_success:
                            print(f"✅ Telegram sent for: {job.get('title', 'Unknown')}")
                        else:
                            print(f"❌ Telegram failed for: {job.get('title', 'Unknown')}")
                        
                        if facebook_success:
                            print(f"✅ Facebook posted for: {job.get('title', 'Unknown')}")
                        else:
                            print(f"❌ Facebook failed for: {job.get('title', 'Unknown')}")
                            
                    except Exception as e:
                        print(f"❌ Notification failed for job {job_id}: {e}")
            
            if new_jobs_count > 0:
                print(f"🎉 {new_jobs_count} new jobs found and notifications sent!")
            else:
                print("ℹ️ No new jobs found")
        
        print("✅ Scraping and enhancement completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Script error: {e}")
    except subprocess.TimeoutExpired:
        print("❌ Script timeout after 5 minutes")
    except Exception as e:
        print(f"❌ Unexpected error in scraping: {e}")

# Initialize scheduler when app starts
if os.environ.get('DYNO'):  # Only in Heroku production
    start_scheduler()
    print("🚀 Scheduler started for production!")

def scheduler_loop():
    schedule.every(6).hours.do(run_scripts)  # 6 hours for production
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every second to avoid delay



if __name__ == "__main__":
    if not os.environ.get('DYNO'):  # Local development only
        threading.Thread(target=scheduler_loop, daemon=True).start()
        app.run(debug=True)
    else:
        # Production - Gunicorn handles the app, scheduler already started above
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
    
