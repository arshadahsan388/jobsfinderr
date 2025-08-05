from flask import Flask, render_template, jsonify, abort, url_for, Response
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

# Initialize scheduler for production
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_scripts, trigger="interval", hours=6)
    scheduler.start()
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

# Load jobs from JSON file
def load_jobs():
    with open("jobs_data/jobs.json", "r", encoding="utf-8") as file:
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

    # ✅ Load all jobs from your existing function
    jobs = load_jobs()  # This loads from jobs_data/jobs.json

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
        subprocess.run(["python", "jobs_data/scrape_jobs.py"], timeout=300)
        subprocess.run(["python", "enhance_jobs.py"], timeout=300)
        print("✅ Scraping completed successfully")
    except Exception as e:
        print(f"❌ Error in scraping: {e}")

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
    
