import os
import csv
import json
import threading
from datetime import date
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SentApplication

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB_BOT_DIR = os.path.join(BASE_DIR, "job_outreach_bot")
LEADS_FILE = os.path.join(JOB_BOT_DIR, "leads.csv")
ENV_FILE = os.path.join(JOB_BOT_DIR, ".env")

# Background task execution state
TASK_STATE = {
    "is_running": False,
    "status": "Idle",
    "progress": 0,
    "total": 0,
    "logs": []
}

def log_msg(msg):
    TASK_STATE["logs"].append(msg)
    if len(TASK_STATE["logs"]) > 200:
        TASK_STATE["logs"].pop(0)

def dashboard(request):
    today = date.today()
    sent_today = SentApplication.objects.filter(sent_date=today).count()
    total_sent = SentApplication.objects.count()
    
    # Read leads count
    leads_count = 0
    sample_leads = []
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, r in enumerate(reader):
                leads_count += 1
                if i < 8:
                    sample_leads.append(r)

    # Read .env details
    config = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip().strip('"').strip("'")

    recent_sent = SentApplication.objects.all()[:15]

    context = {
        "sent_today": sent_today,
        "daily_limit": config.get("DAILY_LIMIT", "200"),
        "total_sent": total_sent,
        "leads_count": leads_count,
        "sample_leads": sample_leads,
        "recent_sent": recent_sent,
        "config": config,
        "task_state": TASK_STATE
    }
    return render(request, "job_agent/dashboard.html", context)


@csrf_exempt
def trigger_fetch_companies(request):
    if request.method == "POST":
        if TASK_STATE["is_running"]:
            return JsonResponse({"status": "error", "message": "A task is already running."})

        count = int(request.POST.get("count", 200))
        role = request.POST.get("role", "Technical Project Manager")

        def worker():
            TASK_STATE["is_running"] = True
            TASK_STATE["status"] = f"Fetching {count} companies for role: {role}..."
            TASK_STATE["logs"] = []
            log_msg(f"🚀 Started lead fetching process (Target: {count})...")
            try:
                import sys
                sys.path.insert(0, JOB_BOT_DIR)
                from fetch_companies import generate_leads
                fetched = generate_leads(target_count=count, default_role=role)
                log_msg(f"✅ Successfully fetched & saved {fetched} companies to leads.csv!")
                TASK_STATE["status"] = f"Complete: {fetched} leads ready."
            except Exception as e:
                log_msg(f"❌ Error during fetch: {str(e)}")
                TASK_STATE["status"] = "Error"
            finally:
                TASK_STATE["is_running"] = False

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return JsonResponse({"status": "success", "message": "Company fetching started in background."})
    return JsonResponse({"status": "error", "message": "POST required."})


@csrf_exempt
def trigger_send_emails(request):
    if request.method == "POST":
        if TASK_STATE["is_running"]:
            return JsonResponse({"status": "error", "message": "A task is already running."})

        dry_run = request.POST.get("dry_run") == "true"

        def worker():
            TASK_STATE["is_running"] = True
            TASK_STATE["status"] = f"Sending emails ({'DRY RUN' if dry_run else 'LIVE'})..."
            TASK_STATE["logs"] = []
            log_msg(f"🚀 Started outreach batch ({'DRY RUN MODE' if dry_run else 'LIVE SENDING'})...")
            try:
                import sys
                sys.path.insert(0, JOB_BOT_DIR)
                import email_bot
                
                # Intercept record_sent to also save into Django SentApplication
                original_record = email_bot.record_sent
                def synced_record(email, company, role, status="SENT"):
                    original_record(email, company, role, status=status)
                    try:
                        SentApplication.objects.update_or_create(
                            recipient_email=email.strip().lower(),
                            defaults={"company_name": company, "role": role, "status": status}
                        )
                    except Exception as err:
                        log_msg(f"DB Sync warning: {err}")

                email_bot.record_sent = synced_record
                email_bot.send_batch(dry_run=dry_run)
                log_msg(f"✨ Batch finished successfully!")
                TASK_STATE["status"] = "Complete: Outreach finished."
            except Exception as e:
                log_msg(f"❌ Outreach error: {str(e)}")
                TASK_STATE["status"] = "Error"
            finally:
                TASK_STATE["is_running"] = False

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return JsonResponse({"status": "success", "message": "Outreach process started in background."})
    return JsonResponse({"status": "error", "message": "POST required."})


def api_task_status(request):
    return JsonResponse(TASK_STATE)
