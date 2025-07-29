import requests
from bs4 import BeautifulSoup, Tag
import json
import os

base_url = "https://remotejobspakistan.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0 Safari/537.36"
}

# Step 1: Extract all job post links from the page
response = requests.get(base_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

post_links = []
posts = soup.find_all("h2", class_="entry-title")
for post in posts:
    if isinstance(post, Tag):
        a_tag = post.find("a")
        if a_tag and isinstance(a_tag, Tag):
            link = a_tag.get("href")
            if link:
                post_links.append(link)

# Step 2: Scrape each job post
all_jobs = []

for i, url in enumerate(post_links):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Job title
    title_tag = soup.find("h1", class_="entry-title")
    title = title_tag.text.strip() if title_tag else "No title"

    # Description (first 300 characters)
    content_div = soup.find("div", class_="td-post-content tagdiv-type")
    description = content_div.get_text(separator=" ", strip=True)[:300] + "..." if content_div else "No content"

    # Application form link
    app_forms = soup.find_all("a")
    app_form_link = None
    for link in app_forms:
        if isinstance(link, Tag) and link.string and "Online Application Form" in link.string:
            app_form_link = link.get("href")
            break

    # Instruction steps
    ol = soup.find("ol", class_="wp-block-list")
    instructions = []
    if ol and isinstance(ol, Tag):
        for li in ol.find_all("li"):
            instructions.append(li.text.strip())

    # Images (pattern-based intelligent matching from ANY source)
    image_urls = []
    # Extract key terms from job title for pattern matching
    title_words = title.lower().replace("-", " ").split()
    title_keywords = [word for word in title_words if len(word) > 3 and word not in ["jobs", "2025", "online", "apply"]]
    
    # Find all img tags on the page
    img_tags = soup.find_all("img")
    for img in img_tags:
        if isinstance(img, Tag):
            # Check for lazy-loaded images (data-src attribute)
            src = img.get("data-src") or img.get("src")
            if src and isinstance(src, str) and src.startswith("http"):  # Only include actual URLs, not base64 placeholders
                
                # INTELLIGENT PATTERN-BASED APPROACH:
                # Include images from ANY domain if they match job-related patterns
                
                # EXCLUDE unwanted images (logos, social media, etc.)
                if any(unwanted in src for unwanted in [
                    "cropped-cropped-Remote-Jobs-Pakistan.png",  # Site logos
                    "Remote-Jobs-Pakistan-1.png", 
                    "Remote-Jobs-Pakistan.png",
                    "FB-GIF.gif",  # Social media GIFs
                    "AVvXsEgVhpeejw9bWulIgr7SlrkgaIoyJCwyXWf7iApKPUkcsJ-AFmMcvXGxVWVamtSE72TbaG27si6Vphy_OzMuSzzwKJT6ipKHI8L-wqLRqMT7aKSrJXW4h4gX9GoRm6vzaxBMTZFz_Ci3-5ff/"
                ]):
                    continue
                
                # INCLUDE images that match job-related patterns:
                
                # 1. Images from known job sites (remotejobspakistan.com)
                if "remotejobspakistan.com/wp-content/uploads" in src:
                    image_urls.append(src)
                
                # 2. Advertisement images from pakistanjobsbank.com
                elif "pakistanjobsbank.com" in src and "Ad_" in src:
                    image_urls.append(src)
                
                # 3. PATTERN MATCHING: Images from ANY domain that contain job-related keywords
                elif any(keyword in src.lower() for keyword in title_keywords) and "2025" in src:
                    image_urls.append(src)
                
                # 4. Specific blogger job images (like PIA s16000/2.jpg)
                elif ("blogger.googleusercontent.com" in src and 
                      "s16000" in src and src.endswith(".jpg")):
                    image_urls.append(src)

    # Table data (if available)
    job_info = {}
    table = soup.find("table")
    if table and isinstance(table, Tag):
        for row in table.find_all("tr"):
            if isinstance(row, Tag):
                cols = row.find_all("td")
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    job_info[key] = value

    # Append to all_jobs list with unique ID
    all_jobs.append({
        "id": i,  # 👈 ID added here (starts from 0)
        "title": title,
        "link": url,
        "description": description,
        "application_form": app_form_link,
        "images": image_urls,  # 👈 Changed from single image to list of images
        "instructions": instructions,
        "details": job_info
    })

# Step 3: Create directory and save to JSON file
os.makedirs("jobs_data", exist_ok=True)
with open("jobs_data/jobs.json", "w", encoding="utf-8") as f:
    json.dump(all_jobs, f, ensure_ascii=False, indent=4)

print("✅ All jobs saved to jobs_data/jobs.json with unique IDs")