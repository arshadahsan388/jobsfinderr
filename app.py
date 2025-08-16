from flask import Flask, render_template, jsonify, abort, url_for, Response, request, redirect
import json
import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import schedule
import time
import threading
import subprocess

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__ ,static_folder='static')

# Scheduler run tracking
last_run_timestamp = None

# Scheduler and status tracking
app.config['SCHEDULER'] = None
last_run_timestamp = None

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
    # Avoid starting multiple schedulers during Flask debug reloader
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or os.environ.get('DYNO'):
        if app.config.get('SCHEDULER'):
            return
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=run_scripts, trigger="interval", hours=6, id='scrape_jobs')
        scheduler.start()
        app.config['SCHEDULER'] = scheduler
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

# Load jobs from JSON file
def load_jobs():
    with open("jobs_enhanced.json", "r", encoding="utf-8") as file:
        jobs = json.load(file)

    # Ensure deterministic added_at for every job so cursor pagination works
    # If missing, set to a decreasing timestamp based on job id to preserve ordering
    base_time = datetime.utcnow()
    for job in jobs:
        if not job.get('added_at'):
            # Use job id as offset seconds to create stable timestamp
            try:
                offset = int(job.get('id', 0))
            except Exception:
                offset = 0
            # Subtract offset seconds from base_time
            job['added_at'] = (base_time.replace(microsecond=0) - timedelta(seconds=offset)).isoformat()

    return jobs

@app.route("/")
def home():
    # Server-side pagination: support cursor-based (preferred) and page-based (for sitemap/GSC)
    jobs = load_jobs()

    # Normalize sort: newest first by added_at if available, fallback to id desc
    def job_sort_key(j):
        # Use ISO added_at if present, else far-past placeholder
        added = j.get('added_at') or ''
        # We want newest first, so sort by added (descending) then id descending
        return (added, j.get('id', 0))

    jobs_sorted = sorted(jobs, key=job_sort_key, reverse=True)

    # Pagination parameters
    PAGE_SIZE = 30
    page = request.args.get('page', type=int)
    cursor = request.args.get('cursor')

    total_jobs = len(jobs_sorted)

    # Page-based (legacy / sitemap friendly)
    if page and page > 0:
        start = (page - 1) * PAGE_SIZE
        paginated = jobs_sorted[start:start + PAGE_SIZE]
        next_page = page + 1 if start + PAGE_SIZE < total_jobs else None
        prev_page = page - 1 if page > 1 else None
        return render_template("index.html", jobs=paginated, total_jobs=total_jobs,
                               page=page, next_page=next_page, prev_page=prev_page)

    # Cursor-based (preferred): cursor is ISO timestamp string representing last seen job added_at
    if cursor:
        # Find first job with added_at strictly less than cursor (jobs_sorted is newest->oldest)
        filtered = [j for j in jobs_sorted if j.get('added_at') and j.get('added_at') < cursor]
        paginated = filtered[:PAGE_SIZE]
        next_cursor = paginated[-1].get('added_at') if len(paginated) == PAGE_SIZE else None
        return render_template("index.html", jobs=paginated, total_jobs=total_jobs,
                               cursor=cursor, next_cursor=next_cursor)

    # Default: first page via cursor (most recent)
    paginated = jobs_sorted[:PAGE_SIZE]
    next_cursor = paginated[-1].get('added_at') if len(paginated) == PAGE_SIZE else None
    return render_template("index.html", jobs=paginated, total_jobs=total_jobs,
                           next_cursor=next_cursor)

        
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
    return render_template("About.html")

@app.route("/contact")
def contact():
    return render_template("Contact.html")

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
    
    # API and Feed endpoints for job aggregators and LLMs
    pages.append({
        "loc": f"{base_url}/rss.xml",
        "lastmod": ten_days_ago,
        "priority": "0.9"
    })
    pages.append({
        "loc": f"{base_url}/feed.json",
        "lastmod": ten_days_ago,
        "priority": "0.9"
    })
    pages.append({
        "loc": f"{base_url}/api/jobs",
        "lastmod": ten_days_ago,
        "priority": "0.8"
    })

    # Load all jobs from enhanced JSON file
    jobs = load_jobs()

    # Add paginated job-list pages to sitemap (page-based pagination)
    PAGE_SIZE = 30
    total_jobs = len(jobs)
    total_pages = (total_jobs + PAGE_SIZE - 1) // PAGE_SIZE
    # Add root list page (page 1) and subsequent pages explicitly
    for p in range(1, total_pages + 1):
        loc = f"{base_url}/" if p == 1 else f"{base_url}/?page={p}"
        pages.append({
            "loc": loc,
            "lastmod": ten_days_ago,
            "priority": "0.8"
        })

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

    # Also write a static sitemap file so you can submit to Google Search Console
    try:
        static_dir = os.path.join(app.root_path, 'static')
        os.makedirs(static_dir, exist_ok=True)
        with open(os.path.join(static_dir, 'sitemap.xml'), 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(sitemap_xml)
    except Exception as e:
        # Log but don't fail sitemap endpoint
        print(f"⚠️ Failed to write static sitemap.xml: {e}")

    response = Response(sitemap_xml, mimetype='application/xml')
    response.headers['Cache-Control'] = 'public, max-age=86400'  # Cache for 1 day
    return response

@app.route('/indexnow-key.txt')
def indexnow_key():
    """Serve IndexNow verification key"""
    return app.send_static_file('jobsfinderr-indexnow-2025.txt')

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt file for search engine crawlers"""
    try:
        with open('robots.txt', 'r', encoding='utf-8') as f:
            robots_content = f.read()
        
        response = Response(robots_content, mimetype='text/plain')
        response.headers['Cache-Control'] = 'public, max-age=86400'  # Cache for 1 day
        return response
    except Exception as e:
        # Fallback robots.txt if file not found
        fallback_robots = """User-agent: *
Allow: /

# Priority pages for search engines
Allow: /government-jobs
Allow: /private-jobs
Allow: /jobs/*
Allow: /job/*
Allow: /about
Allow: /contact
Allow: /privacy-policy

# Sitemap location
Sitemap: https://jobsfinderr.me/sitemap.xml

# High priority job categories
Allow: /jobs/karachi
Allow: /jobs/lahore
Allow: /jobs/islamabad
Allow: /jobs/peshawar
Allow: /jobs/rawalpindi
Allow: /jobs/faisalabad

# Crawl-delay for respectful crawling
Crawl-delay: 1
"""
        response = Response(fallback_robots, mimetype='text/plain')
        response.headers['Cache-Control'] = 'public, max-age=86400'
        return response

@app.route('/ads.txt')
def ads_txt():
    """Serve ads.txt file for advertising networks monetization"""
    try:
        with open('ads.txt', 'r', encoding='utf-8') as f:
            ads_content = f.read()
        
        response = Response(ads_content, mimetype='text/plain')
        response.headers['Cache-Control'] = 'public, max-age=86400'  # Cache for 1 day
        return response
    except Exception as e:
        # Fallback ads.txt with your actual AdSense publisher ID
        fallback_ads = """# Ads.txt for jobsfinderr.me
# This file authorizes who can sell advertising on this website

# Google AdSense - ACTIVE Publisher ID
google.com, pub-6268553487157911, DIRECT, f08c47fec0942fa0

# Additional ad networks can be added here
# Each line format: domain.com, publisher-account-id, relationship, certification-authority

# Media.net (optional)
# media.net, 8CUO9I0PQ, DIRECT

# Note: This file is automatically served at https://jobsfinderr.me/ads.txt
"""
        response = Response(fallback_ads, mimetype='text/plain')
        response.headers['Cache-Control'] = 'public, max-age=86400'
        return response

@app.route('/rss.xml')
def rss_feed():
    """RSS Feed for job aggregators, Google Jobs, and LLMs"""
    try:
        jobs = load_jobs()
        base_url = "https://jobsfinderr.me"
        
        # Create RSS XML structure
        rss = ET.Element('rss', version="2.0")
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
        rss.set('xmlns:dc', 'http://purl.org/dc/elements/1.1/')
        
        channel = ET.SubElement(rss, 'channel')
        
        # Channel metadata
        ET.SubElement(channel, 'title').text = "JobsFindeRR - Latest Jobs in Pakistan"
        ET.SubElement(channel, 'link').text = base_url
        ET.SubElement(channel, 'description').text = "Latest government and private sector job opportunities in Pakistan. Updated daily with fresh job postings."
        ET.SubElement(channel, 'language').text = "en-us"
        ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        ET.SubElement(channel, 'generator').text = "JobsFindeRR RSS Generator"
        ET.SubElement(channel, 'webMaster').text = "admin@jobsfinderr.me (JobsFindeRR Team)"
        ET.SubElement(channel, 'managingEditor').text = "editor@jobsfinderr.me (JobsFindeRR Editorial)"
        ET.SubElement(channel, 'copyright').text = f"Copyright {datetime.now().year} JobsFindeRR. All rights reserved."
        ET.SubElement(channel, 'category').text = "Jobs and Employment"
        
        # Atom self link
        atom_link = ET.SubElement(channel, 'atom:link')
        atom_link.set('href', f"{base_url}/rss.xml")
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')
        
        # Add latest 50 jobs to RSS
        for job in jobs[:50]:
            item = ET.SubElement(channel, 'item')
            
            job_title = job.get('title', 'Untitled Job')
            job_id = job.get('id', 0)
            job_details = job.get('details', {})
            
            # Required RSS elements
            ET.SubElement(item, 'title').text = job_title
            ET.SubElement(item, 'link').text = f"{base_url}/job/{job_id}"
            ET.SubElement(item, 'guid').text = f"{base_url}/job/{job_id}"
            
            # Description with job details
            description = f"""
            <![CDATA[
            <h3>{job_title}</h3>
            <p><strong>Department:</strong> {job_details.get('Department', 'N/A')}</p>
            <p><strong>Location:</strong> {job_details.get('Location', 'Pakistan')}</p>
            <p><strong>Salary:</strong> {job_details.get('Salary', 'As per rules')}</p>
            <p><strong>Education:</strong> {job_details.get('Education', 'As required')}</p>
            <p><strong>Experience:</strong> {job_details.get('Experience', 'Fresh/Experienced')}</p>
            <p><strong>Last Date:</strong> {job_details.get('Last Date for Apply', 'Check details')}</p>
            <p><strong>Job Type:</strong> {job_details.get('Job Type', 'Government')}</p>
            <p><a href="{base_url}/job/{job_id}">View Full Details &amp; Apply</a></p>
            ]]>
            """
            ET.SubElement(item, 'description').text = description
            
            # Additional metadata
            ET.SubElement(item, 'category').text = job_details.get('Job Type', 'Government')
            ET.SubElement(item, 'dc:creator').text = "JobsFindeRR Editorial Team"
            ET.SubElement(item, 'pubDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # Custom namespace for job-specific data
            ET.SubElement(item, 'source').text = "JobsFindeRR.me"
        
        # Convert to string and create response
        rss_xml = ET.tostring(rss, encoding='utf-8', method='xml')
        rss_content = b'<?xml version="1.0" encoding="UTF-8"?>\n' + rss_xml
        
        response = Response(rss_content, mimetype='application/rss+xml')
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        response.headers['Access-Control-Allow-Origin'] = '*'  # Allow cross-origin requests
        return response
        
    except Exception as e:
        return Response(f"Error generating RSS feed: {str(e)}", status=500)

@app.route('/feed.json')
def json_feed():
    """JSON Feed for modern APIs, ChatGPT plugins, and AI bots"""
    try:
        jobs = load_jobs()
        base_url = "https://jobsfinderr.me"
        
        # JSON Feed 1.1 specification
        feed = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": "JobsFindeRR - Pakistan Jobs Feed",
            "home_page_url": base_url,
            "feed_url": f"{base_url}/feed.json",
            "description": "Latest government and private sector job opportunities in Pakistan. Updated daily with comprehensive job details.",
            "icon": f"{base_url}/static/favicon.ico",
            "favicon": f"{base_url}/static/favicon.ico",
            "language": "en",
            "authors": [
                {
                    "name": "JobsFindeRR Editorial Team",
                    "url": base_url
                }
            ],
            "items": []
        }
        
        # Add latest 100 jobs to JSON feed
        for job in jobs[:100]:
            job_title = job.get('title', 'Untitled Job')
            job_id = job.get('id', 0)
            job_details = job.get('details', {})
            job_instructions = job.get('instructions', [])
            
            # Format content as HTML
            content_html = f"""
            <h2>{job_title}</h2>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr><td><strong>Department</strong></td><td>{job_details.get('Department', 'N/A')}</td></tr>
                <tr><td><strong>Location</strong></td><td>{job_details.get('Location', 'Pakistan')}</td></tr>
                <tr><td><strong>Salary</strong></td><td>{job_details.get('Salary', 'As per government rules')}</td></tr>
                <tr><td><strong>Education</strong></td><td>{job_details.get('Education', 'As required')}</td></tr>
                <tr><td><strong>Experience</strong></td><td>{job_details.get('Experience', 'Fresh/Experienced')}</td></tr>
                <tr><td><strong>Age Limit</strong></td><td>{job_details.get('Age', 'As per rules')}</td></tr>
                <tr><td><strong>Total Vacancies</strong></td><td>{job_details.get('Total Vacancies', 'Multiple')}</td></tr>
                <tr><td><strong>Job Type</strong></td><td>{job_details.get('Job Type', 'Government')}</td></tr>
                <tr><td><strong>Last Date</strong></td><td>{job_details.get('Last Date for Apply', 'Check details')}</td></tr>
            </table>
            
            <h3>Application Instructions:</h3>
            <ol>
            """
            
            for instruction in job_instructions:
                content_html += f"<li>{instruction}</li>"
            
            content_html += f"""
            </ol>
            <p><a href="{base_url}/job/{job_id}">Apply Now - View Full Details</a></p>
            """
            
            # Create summary text without HTML
            summary = f"{job_title} - {job_details.get('Department', 'Government Department')} in {job_details.get('Location', 'Pakistan')}. Salary: {job_details.get('Salary', 'Competitive')}. Last date: {job_details.get('Last Date for Apply', 'Check details')}."
            
            item = {
                "id": f"{base_url}/job/{job_id}",
                "url": f"{base_url}/job/{job_id}",
                "title": job_title,
                "content_html": content_html,
                "summary": summary,
                "date_published": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat(),
                "authors": [
                    {
                        "name": "JobsFindeRR Team"
                    }
                ],
                "tags": [
                    job_details.get('Job Type', 'Government'),
                    job_details.get('Location', 'Pakistan'),
                    "Pakistan Jobs",
                    "Employment"
                ],
                "external_url": job.get('application_form', ''),
                "_jobsfinderr": {
                    "job_type": job_details.get('Job Type', 'Government'),
                    "location": job_details.get('Location', 'Pakistan'),
                    "salary": job_details.get('Salary', 'As per rules'),
                    "education": job_details.get('Education', 'Various'),
                    "experience": job_details.get('Experience', 'Fresh/Experienced'),
                    "vacancies": job_details.get('Total Vacancies', 'Multiple'),
                    "last_date": job_details.get('Last Date for Apply', 'TBD'),
                    "department": job_details.get('Department', 'Government')
                }
            }
            
            feed["items"].append(item)
        
        response = jsonify(feed)
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        response.headers['Access-Control-Allow-Origin'] = '*'  # Allow cross-origin requests
        return response
        
    except Exception as e:
        return jsonify({"error": f"Error generating JSON feed: {str(e)}"}), 500

@app.route('/api/jobs')
def api_jobs():
    """REST API endpoint for external integrations"""
    try:
        jobs = load_jobs()
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        job_type = request.args.get('type', '')
        location = request.args.get('location', '')
        
        # Filter jobs
        filtered_jobs = jobs
        
        if job_type:
            filtered_jobs = [job for job in filtered_jobs 
                           if job.get('details', {}).get('Job Type', '').lower() == job_type.lower()]
        
        if location:
            filtered_jobs = [job for job in filtered_jobs 
                           if location.lower() in job.get('details', {}).get('Location', '').lower()]
        
        # Apply pagination
        paginated_jobs = filtered_jobs[offset:offset+limit]
        
        # Format response
        api_response = {
            "status": "success",
            "total_jobs": len(jobs),
            "filtered_jobs": len(filtered_jobs),
            "limit": limit,
            "offset": offset,
            "jobs": []
        }
        
        for job in paginated_jobs:
            job_data = {
                "id": job.get('id'),
                "title": job.get('title'),
                "url": f"https://jobsfinderr.me/job/{job.get('id')}",
                "details": job.get('details', {}),
                "instructions": job.get('instructions', []),
                "application_url": job.get('application_form', ''),
                "posted_date": datetime.now().isoformat()
            }
            api_response["jobs"].append(job_data)
        
        response = jsonify(api_response)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Cache-Control'] = 'public, max-age=1800'  # Cache for 30 minutes
        return response
        
    except Exception as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500

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
    global last_run_timestamp
    print("✅ Running scraping tasks at", datetime.now())
    last_run_timestamp = datetime.utcnow().isoformat()
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
        last_run_timestamp = datetime.utcnow().isoformat()


@app.route('/scheduler-status')
def scheduler_status():
    """Return scheduler running status and last run timestamp"""
    scheduler = app.config.get('SCHEDULER')
    status = {
        'scheduler_running': bool(scheduler and getattr(scheduler, 'running', False)),
        'last_run_utc': last_run_timestamp,
    }
    return jsonify(status)
    return jsonify(status)

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
    
