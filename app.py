from flask import Flask, render_template, jsonify, abort, url_for, Response
import json
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import schedule
import time
import threading
import subprocess

# Import WhatsApp automation
from whatsapp_automation import send_new_job_notification

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__ ,static_folder='static')

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

@app.route("/whatsapp-messages")
def whatsapp_messages():
    """View pending WhatsApp messages"""
    try:
        if os.path.exists("whatsapp_messages.json"):
            with open("whatsapp_messages.json", "r", encoding="utf-8") as f:
                messages = json.load(f)
        else:
            messages = []
        
        # Get recent unsent messages
        recent_messages = [msg for msg in messages if not msg.get('sent', False)][-10:]
        
        html = """
        <h2>📱 WhatsApp Job Notifications</h2>
        <p>Click the links below to manually send job notifications to WhatsApp groups:</p>
        """
        
        if not recent_messages:
            html += "<p>✅ No pending messages</p>"
        else:
            for msg in recent_messages:
                html += f"""
                <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;">
                    <h4>Job ID: {msg.get('id', 'N/A')}</h4>
                    <pre style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 4px;">{msg.get('message', 'N/A')}</pre>
                    <p><strong>Created:</strong> {msg.get('created_at', 'N/A')}</p>
                    <a href="{msg.get('whatsapp_link', '#')}" target="_blank" 
                       style="background: #25D366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                       📱 Send to WhatsApp
                    </a>
                </div>
                """
        
        html += f"""
        <hr>
        <p><a href="/">← Back to Jobs</a> | <a href="/debug-scheduler">Debug Scheduler</a></p>
        <p><small>Last updated: {datetime.now()}</small></p>
        """
        
        return html
        
    except Exception as e:
        return f"❌ Error loading WhatsApp messages: {e}"

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
                <p>Check your Telegram channel/group for the message with WhatsApp share link!</p>
                <p><a href="/test-whatsapp">Test WhatsApp</a> | <a href="/">← Back to Jobs</a></p>
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

@app.route("/test-whatsapp")
def test_whatsapp():
    """Test WhatsApp notification with sample job"""
    try:
        # Get a sample job from current data
        jobs = load_jobs()
        if jobs:
            sample_job = jobs[0]  # Use first job as sample
            success = send_new_job_notification(sample_job)
            
            if success:
                return f"""
                <h2>✅ WhatsApp Test Successful!</h2>
                <p>Test notification sent for: <strong>{sample_job.get('title', 'N/A')}</strong></p>
                <p><a href="/whatsapp-messages">View WhatsApp Messages</a></p>
                <p><a href="/">← Back to Jobs</a></p>
                """
            else:
                return f"""
                <h2>❌ WhatsApp Test Failed</h2>
                <p>Check the console logs for error details.</p>
                <p><a href="/whatsapp-messages">View WhatsApp Messages</a></p>
                <p><a href="/">← Back to Jobs</a></p>
                """
        else:
            return "❌ No jobs available for testing"
            
    except Exception as e:
        return f"❌ Error testing WhatsApp: {e}"


@app.route("/privacy-policy")
def privacy():
    return render_template("privacy_policy.html")

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

    # Static URLs
    pages.append({
        "loc": url_for("home", _external=True),
        "lastmod": ten_days_ago,
    })
    pages.append({
        "loc": url_for("about", _external=True),
        "lastmod": ten_days_ago,
    })
    pages.append({
        "loc": url_for("contact", _external=True),
        "lastmod": ten_days_ago,
    })
    pages.append({
        "loc": url_for("privacy", _external=True),
        "lastmod": ten_days_ago,
    })

    # ✅ Load all jobs from enhanced JSON file
    jobs = load_jobs()  # This now loads from jobs_enhanced.json

    for job in jobs:
        pages.append({
            "loc": url_for("job_detail", job_id=job['id'], _external=True),
            "lastmod": ten_days_ago,
        })

    # XML generation
    xml = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for page in pages:
        url = ET.SubElement(xml, 'url')
        ET.SubElement(url, 'loc').text = page["loc"]
        ET.SubElement(url, 'lastmod').text = page["lastmod"]
        ET.SubElement(url, 'changefreq').text = "weekly"
        ET.SubElement(url, 'priority').text = "0.8"

    sitemap_xml = ET.tostring(xml, encoding="utf-8", method="xml")
    return Response(sitemap_xml, mimetype='application/xml')



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
                    # This is a new job - send notifications
                    try:
                        # WhatsApp notification (saves for manual sending)
                        send_new_job_notification(job)
                        
                        # Telegram notification (automatic)
                        from telegram_bot import send_telegram_job_notification
                        telegram_success = send_telegram_job_notification(job)
                        
                        new_jobs_count += 1
                        print(f"📱 WhatsApp prepared for: {job.get('title', 'Unknown')}")
                        if telegram_success:
                            print(f"📡 Telegram sent for: {job.get('title', 'Unknown')}")
                            
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
    
