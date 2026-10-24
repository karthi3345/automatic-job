"""
Daily Production Scheduler for Job Outreach Bot
Designed to run 24/7 on your local PC / mini-PC.

Schedule:
- Runs automatically every morning (default: 09:30 AM local time) Monday through Friday.
- Automatically fetches fresh company leads.
- Automatically sends up to 200 tailored applications via Gmail SMTP.
- Handles sleep, power resumption, and error retries.
"""

import os
import sys
import time
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from fetch_companies import generate_leads
from email_bot import send_batch, get_sent_today_count

TARGET_HOUR = 9     # 9 AM
TARGET_MINUTE = 30  # 9:30 AM
DEFAULT_ROLE = "Technical Project Manager"
DAILY_TARGET = 200


def run_daily_job(dry_run=False):
    print("\n" + "=" * 65)
    print(f"⏰ [CRON TRIGGERED] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Goal: Deliver daily batch of {DAILY_TARGET} applications for '{DEFAULT_ROLE}'")
    print("=" * 65)

    # 1. Check if already reached today
    sent_already = get_sent_today_count()
    if sent_already >= DAILY_TARGET:
        print(f"✅ Daily limit of {DAILY_TARGET} already achieved today ({sent_already} sent). Skipping.")
        return

    # 2. Fetch leads
    print("\n[Step 1/2] Fetching fresh companies...")
    try:
        generate_leads(target_count=DAILY_TARGET, default_role=DEFAULT_ROLE)
    except Exception as e:
        print(f"⚠️ Warning during lead fetch: {e}")

    # 3. Send emails
    print("\n[Step 2/2] Initiating email batch...")
    try:
        send_batch(dry_run=dry_run)
    except Exception as e:
        print(f"❌ Error during email delivery: {e}")

    print("\n🏁 Daily run completed. Waiting for next scheduled run window.\n")


def start_scheduler(dry_run=False, run_immediate=False):
    print("=" * 65)
    print("🤖 24/7 PRODUCTION SCHEDULER ACTIVE")
    print(f"📅 Scheduled to trigger daily at: {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} AM (Mon - Fri)")
    print(f"⚙️ Mode: {'DRY RUN' if dry_run else 'PRODUCTION (LIVE GMAIL)'}")
    print("=" * 65)

    if run_immediate:
        print("⚡ Run immediate flag detected. Triggering batch now...")
        run_daily_job(dry_run=dry_run)

    last_run_day = None

    while True:
        now = datetime.now()
        current_day = now.date()

        # Monday is 0, Sunday is 6. Run Mon-Fri (or Mon-Sat)
        is_weekday = now.weekday() < 6

        # Check if it's trigger time and hasn't run yet today
        if is_weekday and now.hour == TARGET_HOUR and now.minute == TARGET_MINUTE and last_run_day != current_day:
            last_run_day = current_day
            run_daily_job(dry_run=dry_run)

        # Heartbeat sleep 30 seconds
        time.sleep(30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="24/7 Background Scheduler for Job Outreach")
    parser.add_argument("--dry-run", action="store_true", help="Simulate email sending without real emails")
    parser.add_argument("--now", action="store_true", help="Run once immediately, then continue listening on schedule")
    args = parser.parse_args()

    try:
        start_scheduler(dry_run=args.dry_run, run_immediate=args.now)
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user.")
