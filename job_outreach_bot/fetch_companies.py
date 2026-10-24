"""
Company & HR Lead Fetcher
Fetches tech companies hiring actively and formats them for job outreach.
Sources:
- poteto/hiring-without-whiteboards (740+ curated tech companies)
- RemoteOK & Jobicy APIs
- Validates active domains to prevent dead emails
"""

import re
import csv
import socket
import os
import requests
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_FILE = os.path.join(BASE_DIR, "leads.csv")

GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/poteto/hiring-without-whiteboards/master/README.md",
    "https://raw.githubusercontent.com/lukasz-madon/awesome-remote-job/master/README.md"
]

ATS_DOMAINS = [
    "lever.co", "greenhouse.io", "workable.com", "rippling.com", 
    "smartrecruiters.com", "bamboohr.com", "myworkdayjobs.com", "ashbyhq.com"
]


def domain_is_live(domain):
    """Verifies domain DNS resolves to prevent sending to dead domains."""
    try:
        socket.gethostbyname(domain)
        return True
    except:
        return False


def fetch_from_hiring_repos():
    """Extracts companies from curated public hiring repositories."""
    companies = []
    seen_domains = set()

    for url in GITHUB_SOURCES:
        try:
            print(f"📡 Fetching companies from {url.split('/')[-2]}...")
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue

            lines = resp.text.split("\n")
            for line in lines:
                if "http" not in line:
                    continue

                matches = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', line)
                for name, link in matches:
                    name = name.strip()
                    # Skip common markdown link labels, articles, blog posts, and non-company text
                    skip_words = [
                        "http", "here", "apply", "careers", "link", "source", "website", 
                        "interview", "hiring", "talent", "hackernews", "article", "post", 
                        "blog", "guide", "talk", "video", "how i hire", "how to hire", "alternative"
                    ]
                    if any(x in name.lower() for x in skip_words):
                        continue

                    # Skip names that are too long (likely article titles)
                    if len(name.split()) > 4:
                        continue

                    netloc = urlparse(link).netloc.replace("www.", "").lower()
                    if not netloc or "." not in netloc:
                        continue

                    # Filter out ATS aggregators and social networks
                    if any(ats in netloc for ats in ATS_DOMAINS) or any(s in netloc for s in ["github.com", "linkedin.com", "twitter.com", "medium.com"]):
                        continue

                    if netloc not in seen_domains:
                        seen_domains.add(netloc)
                        companies.append({
                            "company_name": name,
                            "domain": netloc,
                            "source_url": link
                        })
        except Exception as e:
            print(f"⚠️ Error fetching from {url}: {e}")

    return companies


def fetch_remoteok_jobs():
    """Fetches live active tech jobs from RemoteOK."""
    leads = []
    try:
        print("📡 Fetching active listings from RemoteOK API...")
        res = requests.get("https://remoteok.com/api", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code == 200:
            data = res.json()[1:]  # First element is legal notice
            for item in data:
                company = item.get("company", "").strip()
                position = item.get("position", "").strip()
                desc = item.get("description", "")
                
                # Check for explicit recruiter email in job post
                emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', desc)
                valid_emails = [
                    e.strip(".").lower() for e in emails 
                    if not any(e.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".js", ".css"])
                ]

                if valid_emails:
                    leads.append({
                        "recipient_name": "Hiring Team",
                        "recipient_email": valid_emails[0],
                        "company_name": company,
                        "role": position or "Technical Project Manager"
                    })
    except Exception as e:
        print(f"⚠️ RemoteOK fetch notice: {e}")

    return leads


def generate_leads(target_count=200, default_role="Technical Project Manager"):
    """
    Main function to automatically discover companies,
    construct hiring contact addresses, verify domain health, and save to leads.csv.
    """
    print(f"\n🔍 Starting automated lead discovery (Target: {target_count} companies)...")
    
    discovered_leads = []
    seen_emails = set()

    # 1. Fetch any explicit hiring emails from RemoteOK first
    remote_leads = fetch_remoteok_jobs()
    for rl in remote_leads:
        em = rl["recipient_email"].lower()
        if em not in seen_emails:
            seen_emails.add(em)
            discovered_leads.append(rl)

    print(f"✅ Found {len(discovered_leads)} direct recruiter emails from job postings.")

    # 2. Fetch curated tech companies from hiring directories
    companies = fetch_from_hiring_repos()
    print(f"🏢 Discovered {len(companies)} tech companies from verified hiring repositories.")

    print("🔎 Verifying company domains and generating contact routes...")
    for comp in companies:
        if len(discovered_leads) >= target_count:
            break

        domain = comp["domain"]
        cname = comp["company_name"]

        # Fast DNS check
        if not domain_is_live(domain):
            continue

        # Standard industry career and recruitment inboxes
        target_email = f"careers@{domain}".lower()
        if target_email not in seen_emails:
            seen_emails.add(target_email)
            discovered_leads.append({
                "recipient_name": f"{cname} Hiring Team",
                "recipient_email": target_email,
                "company_name": cname,
                "role": default_role
            })

    # Save to leads.csv
    with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["recipient_name", "recipient_email", "company_name", "role"])
        writer.writeheader()
        for row in discovered_leads:
            writer.writerow(row)

    print(f"\n🎉 Successfully auto-fetched and saved {len(discovered_leads)} verified company leads into:")
    print(f"👉 {LEADS_FILE}\n")
    return len(discovered_leads)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-fetch companies and recruiters for job applications")
    parser.add_argument("--count", type=int, default=200, help="Number of leads to fetch (default: 200)")
    parser.add_argument("--role", type=str, default="Technical Project Manager", help="Target role")
    args = parser.parse_args()

    generate_leads(target_count=args.count, default_role=args.role)
