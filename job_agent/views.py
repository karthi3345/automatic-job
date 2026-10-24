import os
import csv
import json
import re
from urllib.parse import quote, urlparse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JobLead, SentApplication
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB_BOT_DIR = os.path.join(BASE_DIR, "job_outreach_bot")
LEADS_FILE = os.path.join(JOB_BOT_DIR, "leads.csv")

SENDER_NAME = "Karthik Raja L"
SENDER_EMAIL = "lkarthikaraja@gmail.com"
PORTFOLIO = "https://dashing-praline-9e34ab.netlify.app/"
GITHUB = "https://github.com/karthi3345"
PHONE = "+91 8610177637"

RESUME_ONLINE_URL = "https://automatic-job.vercel.app/resume/"

def build_gmail_web_link(email, company, role):
    """Generates a direct Gmail compose web link: https://mail.google.com/mail/?view=cm..."""
    subject = f"Application: {role} - {SENDER_NAME} (Technical PM - 4+ Years Exp)"
    body = f"""Dear Hiring Team,

I hope this email finds you well.

I am writing to express my strong interest in open {role} opportunities at {company}.

With over 4+ years of experience as a Technical Project Coordinator / Project Manager driving end-to-end delivery of complex platforms (AI/ML, FinTech/Banking, Gaming, IoT, and Enterprise systems), I bridge business requirements and hands-on engineering execution.

Key Highlights:
• Agile Scrum Delivery: Owned sprint planning, backlog grooming, JIRA burn-down tracking, and production releases.
• Technical Depth: Python (Django/DRF), REST APIs, SQL (PostgreSQL), and Cloud Deployments (AWS).
• Proven Project History: Coordinated AI-based Stock Prediction Platform (Django/React/RNN), Banking KYC Applications, and IoT Control Systems.
• Governance: Expert in RAID logs, UAT governance, and cross-functional team alignment.

📄 Resume / CV Direct PDF Link: {RESUME_ONLINE_URL}
🌐 Portfolio: {PORTFOLIO}
🔗 GitHub: {GITHUB}

I would welcome the opportunity to connect and discuss how my skills align with your needs at {company}.

Warm regards,

{SENDER_NAME}
Technical Project Manager / Project Coordinator
Phone: {PHONE}
Email: {SENDER_EMAIL}
"""
    params = {
        "view": "cm",
        "fs": "1",
        "to": email,
        "su": subject,
        "body": body
    }
    from urllib.parse import urlencode
    return f"https://mail.google.com/mail/?{urlencode(params)}"


def fetch_live_pm_jobs_from_web():
    """Fetches real Project Manager openings from curated 1000 startup companies, RemoteOK, and Arbeitnow."""
    leads = []
    seen = set()

    # 1. Load 1000 Global Tech Startups (seed file)
    seed_file = os.path.join(os.path.dirname(__file__), "seed_startups.json")
    if os.path.exists(seed_file):
        try:
            with open(seed_file, "r", encoding="utf-8") as f:
                startups = json.load(f)
                for item in startups:
                    cname = item.get("company_name", "").strip()
                    key = f"{cname}-pm".lower()
                    if key not in seen:
                        seen.add(key)
                        leads.append(item)
        except Exception as e:
            print(f"Error loading seed startups: {e}")

    # 1. Fetch RemoteOK
    try:
        r = requests.get("https://remoteok.com/api", headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
        if r.status_code == 200:
            data = r.json()[1:]
            for item in data:
                title = item.get("position", "")
                company = item.get("company", "").strip()
                desc = item.get("description", "")
                if any(k in title.lower() for k in ["project", "program", "product", "delivery", "scrum", "agile", "coordinator"]):
                    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', desc)
                    email = emails[0].strip(".").lower() if emails else ""
                    key = f"{company}-{title}".lower()
                    if key not in seen:
                        seen.add(key)
                        leads.append({
                            "company_name": company,
                            "role": title,
                            "contact_email": email or f"careers@{urlparse(item.get('url', '')).netloc.replace('www.', '')}" if item.get('url') else "",
                            "apply_url": item.get("apply_url") or item.get("url") or "",
                            "source": "RemoteOK Live",
                            "location": item.get("location") or "Remote"
                        })
    except Exception as e:
        print(f"RemoteOK fetch note: {e}")

    # 2. Fetch Arbeitnow
    try:
        r = requests.get("https://arbeitnow.com/api/job-board-api", timeout=6)
        if r.status_code == 200:
            data = r.json().get("data", [])
            for item in data:
                title = item.get("title", "")
                company = item.get("company_name", "").strip()
                if any(k in title.lower() for k in ["project", "program", "delivery", "scrum", "agile"]):
                    key = f"{company}-{title}".lower()
                    if key not in seen:
                        seen.add(key)
                        leads.append({
                            "company_name": company,
                            "role": title,
                            "contact_email": f"jobs@{urlparse(item.get('url', '')).netloc.replace('www.', '')}" if item.get('url') else "",
                            "apply_url": item.get("url") or "",
                            "source": "Arbeitnow Tech",
                            "location": item.get("location") or "Remote / Europe"
                        })
    except Exception as e:
        print(f"Arbeitnow fetch note: {e}")

    # 3. Read leads.csv curated companies
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cname = row.get("company_name", "").strip()
                    role = row.get("role", "Technical Project Manager").strip()
                    email = row.get("recipient_email", "").strip()
                    key = f"{cname}-{role}".lower()
                    if key not in seen:
                        seen.add(key)
                        leads.append({
                            "company_name": cname,
                            "role": role,
                            "contact_email": email,
                            "apply_url": "",
                            "source": "Curated Tech Company",
                            "location": "Global / Remote"
                        })
        except Exception as e:
            print(f"leads.csv read note: {e}")

    return leads


def dashboard(request):
    search_q = request.GET.get("q", "").strip().lower()

    # If database is empty, seed it with 1000 startups
    if JobLead.objects.count() == 0:
        fresh_leads = fetch_live_pm_jobs_from_web()
        to_create = []
        for l in fresh_leads[:1000]:
            to_create.append(JobLead(
                company_name=l["company_name"],
                role=l["role"],
                contact_email=l["contact_email"],
                apply_url=l["apply_url"],
                source=l["source"],
                location=l["location"]
            ))
        JobLead.objects.bulk_create(to_create)

    leads_qs = JobLead.objects.all()
    if search_q:
        leads_qs = leads_qs.filter(
            models.Q(company_name__icontains=search_q) |
            models.Q(role__icontains=search_q) |
            models.Q(location__icontains=search_q)
        )

    # Always ensure every row has a direct action
    display_leads = []
    for lead in leads_qs[:1000]:
        has_direct_email = bool(lead.contact_email and '@' in lead.contact_email)
        apply_url = lead.apply_url or f"https://www.google.com/search?q={quote(lead.company_name + ' careers')}"
        display_leads.append({
            "id": lead.id,
            "company_name": lead.company_name,
            "role": lead.role,
            "contact_email": lead.contact_email,
            "apply_url": apply_url,
            "source": lead.source,
            "location": lead.location,
            "status": lead.status,
            "has_email": has_direct_email,
            "mailto_url": build_gmail_web_link(lead.contact_email, lead.company_name, lead.role) if has_direct_email else ""
        })

    total_leads = JobLead.objects.count()
    applied_count = JobLead.objects.filter(status="EMAILED").count()

    context = {
        "leads": display_leads,
        "total_leads": total_leads,
        "applied_count": applied_count,
        "search_q": search_q,
        "sender_name": SENDER_NAME,
        "portfolio": PORTFOLIO,
        "github": GITHUB
    }
    return render(request, "job_agent/dashboard.html", context)


@csrf_exempt
def refresh_leads_api(request):
    """Force re-fetch new Project Manager jobs."""
    JobLead.objects.all().delete()
    fresh_leads = fetch_live_pm_jobs_from_web()
    to_create = []
    for l in fresh_leads:
        to_create.append(JobLead(
            company_name=l["company_name"],
            role=l["role"],
            contact_email=l["contact_email"],
            apply_url=l["apply_url"],
            source=l["source"],
            location=l["location"]
        ))
    JobLead.objects.bulk_create(to_create)
    return JsonResponse({"status": "success", "count": len(to_create)})


@csrf_exempt
def mark_applied_api(request, lead_id):
    """Marks a lead as applied/emailed."""
    try:
        lead = JobLead.objects.get(id=lead_id)
        lead.status = "EMAILED"
        lead.save()
        return JsonResponse({"status": "success"})
    except JobLead.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Lead not found"})

def serve_resume_pdf(request):
    """Directly serves Karthik Raja's PDF resume."""
    pdf_path = os.path.join(BASE_DIR, "job_agent", "static", "job_agent", "Karthik_Raja_Resume.pdf")
    if os.path.exists(pdf_path):
        from django.http import FileResponse
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return redirect(PORTFOLIO)

