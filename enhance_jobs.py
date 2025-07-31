import json

# Load existing jobs
with open("jobs_data/jobs.json", "r", encoding="utf-8") as file:
    jobs = json.load(file)

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

# Add summary to each job
for job in jobs:
    job["summary"] = generate_summary(job)

# Save enhanced jobs to new file
with open("jobs_enhanced.json", "w", encoding="utf-8") as outfile:
    json.dump(jobs, outfile, indent=2, ensure_ascii=False)

print("✅ Summaries added and saved to 'jobs_enhanced.json'")
