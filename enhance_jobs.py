import json
import os
from datetime import datetime

# Load new jobs from scraping
with open("jobs_data/jobs.json", "r", encoding="utf-8") as file:
    new_jobs = json.load(file)

# Function to parse date and check if it's still valid
def is_job_still_valid(job):
    try:
        last_date = job.get("details", {}).get("Last Date for Apply", "")
        if not last_date:
            return False
        
        # Try different date formats
        date_formats = [
            "%d %B %Y",      # "15 August 2025"
            "%d-%m-%Y",      # "15-08-2025"
            "%d/%m/%Y",      # "15/08/2025"
            "%B %d, %Y",     # "August 15, 2025"
            "%Y-%m-%d",      # "2025-08-15"
        ]
        
        parsed_date = None
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(last_date, date_format)
                break
            except ValueError:
                continue
        
        if parsed_date:
            return parsed_date.date() >= datetime.now().date()
        return False
    except:
        return False

# Load existing enhanced jobs if file exists
existing_jobs = []
if os.path.exists("jobs_enhanced.json"):
    try:
        with open("jobs_enhanced.json", "r", encoding="utf-8") as file:
            existing_jobs = json.load(file)
    except:
        existing_jobs = []

# Filter existing jobs to keep only those with valid dates
valid_existing_jobs = [job for job in existing_jobs if is_job_still_valid(job)]

print(f"📅 Found {len(valid_existing_jobs)} existing jobs with valid dates")
print(f"🆕 Found {len(new_jobs)} new jobs from scraping")

# Summary generator function
def generate_summary(job):
    title = job.get("title", "Job Opportunity")
    location = job.get("details", {}).get("Location", "Pakistan")
    gender = job.get("details", {}).get("Gender", "")
    education = job.get("details", {}).get("Education", "")
    total = job.get("details", {}).get("Total Vacancies", "")
    experience = job.get("details", {}).get("Experience", "")
    salary = job.get("details", {}).get("Salary", "")
    deadline = job.get("details", {}).get("Last Date for Apply", "")

    summary = (
        f"{title} are now open in {location}"
    )

    if gender:
        summary += f" for {gender}"
    if education:
        summary += f" candidates with qualifications ranging from {education}."
    else:
        summary += "."

    if total:
        summary += f" A total of {total} positions are available"
    else:
        summary += f" Multiple positions are available"

    if experience:
        summary += f" for individuals with {experience} experience."
    else:
        summary += "."

    if salary:
        summary += f" The offered salary ranges from {salary}."
    if deadline:
        summary += f" Apply before {deadline}."

    return summary

# Add summary to each new job and create unique IDs
next_id = len(valid_existing_jobs)  # Start IDs after existing jobs
for i, job in enumerate(new_jobs):
    job["summary"] = generate_summary(job)
    job["id"] = next_id + i  # Assign unique ID

# Check for duplicates based on title and link to avoid adding same jobs
existing_links = {job.get("link", "") for job in valid_existing_jobs}
unique_new_jobs = []

for job in new_jobs:
    job_link = job.get("link", "")
    if job_link not in existing_links:
        unique_new_jobs.append(job)
    else:
        print(f"🔄 Skipping duplicate job: {job.get('title', 'Unknown')}")

# Combine valid existing jobs with unique new jobs
all_jobs = valid_existing_jobs + unique_new_jobs

print(f"✅ Final result: {len(all_jobs)} total jobs ({len(valid_existing_jobs)} existing + {len(unique_new_jobs)} new)")

# Save enhanced jobs to file
with open("jobs_enhanced.json", "w", encoding="utf-8") as outfile:
    json.dump(all_jobs, outfile, indent=2, ensure_ascii=False)

print("✅ Jobs merged and saved to 'jobs_enhanced.json'")
print(f"📊 Preserved {len(valid_existing_jobs)} jobs with valid deadlines")
print(f"🆕 Added {len(unique_new_jobs)} new unique jobs")
