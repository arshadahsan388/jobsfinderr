"""
Helper functions for JobsFindeRR application
"""
import re
import hashlib

def create_job_slug(job):
    """Create stable URL slug from job data"""
    title = job.get('title', 'job')
    # Clean title and create URL-friendly slug
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug.lower()[:50]  # Limit length
    # Add short hash for uniqueness
    hash_part = hashlib.md5(job.get('link', title).encode()).hexdigest()[:8]
    return f"{slug}-{hash_part}"
