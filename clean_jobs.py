import json

# Load current jobs
with open('jobs_enhanced.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

print(f'🔍 Checking {len(jobs)} jobs for remotejobspakistan links...')

# Check and fix remotejobspakistan links
fixed_count = 0
for job in jobs:
    if job.get('application_form') and 'remotejobspakistan.com' in str(job.get('application_form')):
        print(f'❌ Found remotejobspakistan link in job: {job.get("title", "Unknown")}')
        job['application_form'] = None  # Remove the fake link
        fixed_count += 1
    elif not job.get('application_form') or job.get('application_form') == 'None':
        job['application_form'] = None  # Ensure it's properly None

print(f'✅ Fixed {fixed_count} jobs with remotejobspakistan links')

# Save cleaned jobs
with open('jobs_enhanced.json', 'w', encoding='utf-8') as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)

print('✅ Jobs cleaned and saved!')
print('🎯 Now when application_form is None, no Apply button will show!')
