"""
Automated Job Outreach Bot via Gmail SMTP (100% Free)
Features:
- Reads targets from leads.csv
- Tracks sent emails in sent_history.db to avoid duplicate messaging
- Enforces daily limit (e.g. 200 emails)
- Adds randomized human-like delays (jitter) to protect Google sender reputation
- Attaches Resume PDF automatically
- Supports dry-run testing before sending real emails
"""

import os
import sys
import csv
import time
import random
import smtplib
import sqlite3
import argparse
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "sent_history.db")
ENV_FILE = os.path.join(BASE_DIR, ".env")


def load_env():
    """Loads configuration from .env file or environment variables."""
    config = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip().strip('"').strip("'")
    
    # Environment variables override .env
    for k, v in os.environ.items():
        config[k] = v
        
    return config


def init_db():
    """Initializes the SQLite database to record sent applications."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sent_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_email TEXT UNIQUE,
            company_name TEXT,
            role TEXT,
            sent_date TEXT,
            sent_timestamp TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_sent_today_count():
    """Returns number of emails sent today."""
    today_str = date.today().isoformat()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM sent_emails WHERE sent_date = ? AND status = 'SENT'", (today_str,))
    count = c.fetchone()[0]
    conn.close()
    return count


def is_already_sent(email):
    """Checks if email has already been contacted previously."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM sent_emails WHERE LOWER(recipient_email) = LOWER(?) AND status = 'SENT'", (email.strip(),))
    row = c.fetchone()
    conn.close()
    return row is not None


def record_sent(email, company, role, status="SENT"):
    """Records the email as sent in database."""
    today_str = date.today().isoformat()
    now_str = datetime.now().isoformat()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO sent_emails 
        (recipient_email, company_name, role, sent_date, sent_timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (email.strip().lower(), company, role, today_str, now_str, status))
    conn.commit()
    conn.close()


def load_file_content(filepath, fallback=""):
    """Reads template file."""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return fallback


def create_email_message(sender_email, sender_name, recipient_email, subject, body, resume_path=None):
    """Creates a multipart MIME email with optional PDF attachment."""
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain", "utf-8"))

    if resume_path and os.path.exists(resume_path):
        part = MIMEBase("application", "octet-stream")
        with open(resume_path, "rb") as attachment:
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        filename = os.path.basename(resume_path)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)
    elif resume_path:
        print(f"  [!] Warning: Resume file '{resume_path}' not found. Sending without attachment.")

    return msg


def send_batch(dry_run=False):
    """Main workflow to process leads and send emails."""
    init_db()
    config = load_env()

    sender_email = config.get("SENDER_EMAIL", "").strip()
    sender_pass = config.get("SENDER_APP_PASSWORD", "").strip()
    sender_name = config.get("SENDER_NAME", "Job Applicant")
    sender_phone = config.get("SENDER_PHONE", "")
    sender_linkedin = config.get("SENDER_LINKEDIN", "")
    sender_portfolio = config.get("SENDER_PORTFOLIO", "")
    sender_github = config.get("SENDER_GITHUB", "")
    resume_path_rel = config.get("RESUME_PATH", "resume.pdf")
    resume_path = os.path.join(BASE_DIR, resume_path_rel) if not os.path.isabs(resume_path_rel) else resume_path_rel

    daily_limit = int(config.get("DAILY_LIMIT", 200))
    min_delay = int(config.get("MIN_DELAY_SECONDS", 25))
    max_delay = int(config.get("MAX_DELAY_SECONDS", 60))

    leads_path = os.path.join(BASE_DIR, "leads.csv")
    subject_tmpl = load_file_content(os.path.join(BASE_DIR, "email_subject.txt"), "Job Application - {sender_name}")
    body_tmpl = load_file_content(os.path.join(BASE_DIR, "email_template.txt"), "Hi {recipient_name},\n\nInterested in {role} at {company_name}.")

    if not dry_run:
        if not sender_email or "your_email" in sender_email or not sender_pass or "xxxx" in sender_pass:
            print("❌ Error: Please configure your SENDER_EMAIL and SENDER_APP_PASSWORD in job_outreach_bot/.env first.")
            print("Tip: Run with --dry-run to test templates and leads without sending actual emails.")
            sys.exit(1)

    if not os.path.exists(leads_path):
        print(f"❌ Error: {leads_path} not found.")
        sys.exit(1)

    sent_today = get_sent_today_count()
    remaining_today = max(0, daily_limit - sent_today)
    print(f"==================================================")
    print(f"🎯 Job Outreach Bot {'[DRY RUN MODE]' if dry_run else '[LIVE MODE]'}")
    print(f"📅 Emails sent today: {sent_today}/{daily_limit} (Remaining quota: {remaining_today})")
    print(f"==================================================")

    if remaining_today <= 0:
        print("🛑 Daily limit reached for today. Come back tomorrow or increase DAILY_LIMIT in .env.")
        return

    leads = []
    with open(leads_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)

    print(f"📋 Total leads found in leads.csv: {len(leads)}")

    # Filter out already sent
    pending_leads = [
        lead for lead in leads 
        if lead.get("recipient_email") and not is_already_sent(lead.get("recipient_email"))
    ]
    print(f"📬 Pending (unsent) leads: {len(pending_leads)}")

    if not pending_leads:
        print("✅ All leads in your CSV have already been emailed! Add new leads to leads.csv.")
        return

    # Connect to SMTP server if live
    server = None
    if not dry_run:
        print("Connecting to Gmail SMTP (smtp.gmail.com:587)...")
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(sender_email, sender_pass)
            print("✅ Successfully authenticated with Gmail SMTP!\n")
        except Exception as e:
            print(f"❌ SMTP Connection / Login failed: {e}")
            print("Make sure you are using an App Password from https://myaccount.google.com/apppasswords")
            sys.exit(1)

    sent_in_this_run = 0

    try:
        for idx, lead in enumerate(pending_leads, start=1):
            if sent_in_this_run >= remaining_today:
                print(f"\n🛑 Daily limit reached ({daily_limit} total today). Stopping current run.")
                break

            recipient_email = lead.get("recipient_email", "").strip()
            recipient_name = lead.get("recipient_name", "Hiring Team").strip() or "Hiring Team"
            company_name = lead.get("company_name", "your company").strip() or "your company"
            role = lead.get("role", "Software Engineer").strip() or "Software Engineer"

            format_vars = {
                "recipient_name": recipient_name,
                "recipient_email": recipient_email,
                "company_name": company_name,
                "role": role,
                "sender_name": sender_name,
                "sender_email": sender_email,
                "sender_phone": sender_phone,
                "sender_linkedin": sender_linkedin,
                "sender_portfolio": sender_portfolio,
                "sender_github": sender_github
            }

            subject = subject_tmpl.format(**format_vars).strip()
            body = body_tmpl.format(**format_vars).strip()

            print(f"[{sent_in_this_run + 1}/{remaining_today}] Sending to: {recipient_name} <{recipient_email}> ({company_name} - {role})...")

            if dry_run:
                print(f"   [DRY RUN] Subject: {subject}")
                print(f"   [DRY RUN] Attachment: {os.path.basename(resume_path)} ({'Found' if os.path.exists(resume_path) else 'Not Found'})")
                record_sent(recipient_email, company_name, role, status="DRY_RUN_TEST")
                sent_in_this_run += 1
            else:
                try:
                    msg = create_email_message(
                        sender_email=sender_email,
                        sender_name=sender_name,
                        recipient_email=recipient_email,
                        subject=subject,
                        body=body,
                        resume_path=resume_path
                    )
                    server.send_message(msg)
                    record_sent(recipient_email, company_name, role, status="SENT")
                    sent_in_this_run += 1
                    print(f"   ✅ Sent successfully!")
                except Exception as ex:
                    print(f"   ❌ Failed to send to {recipient_email}: {ex}")
                    continue

            # Polite delay between emails to protect account reputation
            if idx < len(pending_leads) and sent_in_this_run < remaining_today:
                if dry_run:
                    print("   [DRY RUN] Skipping delay.")
                else:
                    delay = random.randint(min_delay, max_delay)
                    print(f"   ⏳ Waiting {delay}s before next email to protect sender reputation...")
                    time.sleep(delay)

    finally:
        if server:
            server.quit()

    print("\n==================================================")
    print(f"✨ Run completed! Emails processed: {sent_in_this_run}")
    print(f"📊 Check 'sent_history.db' for log of all sent applications.")
    print("==================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Job Application Outreach Bot")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without actually sending emails")
    args = parser.parse_args()

    send_batch(dry_run=args.dry_run)
