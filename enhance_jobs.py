import json
import requests
import time

# Your OpenRouter API Key
API_KEY = "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"

# Load the jobs from JSON
with open("jobs_data/jobs.json", "r", encoding="utf-8") as file:
    jobs = json.load(file)

# Loop through each job and enhance
for job in jobs:
    job_details = f"Title: {job['title']}\nLink: {job['link']}\nEducation: {job['details'].get('Education')}\nLocation: {job['details'].get('Location')}\nExperience: {job['details'].get('Experience')}\nLast Date: {job['details'].get('Last Date for Apply')}\nInstructions: {'; '.join(job['instructions'])}"

    prompt = f"""
You are an expert job content enhancer. Based on the following government job details, generate:

1. A short summary in 2–3 lines
2. 5 relevant keywords

Job Details:
{job_details}
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mixtral-8x7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
    )

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        print(f"\n--- Enhancement for Job ID {job['id']} ---\n{content}")

        # Save enhancement
        job["enhanced_summary"] = content
    else:
        print(f"Failed on job ID {job['id']}:", response.text)

    # Delay to avoid rate limits
    time.sleep(1.5)

# Save enhanced jobs back to file
with open("jobs_enhanced.json", "w", encoding="utf-8") as file:
    json.dump(jobs, file, indent=2, ensure_ascii=False)

print("\n✅ All jobs enhanced and saved to jobs_enhanced.json")
