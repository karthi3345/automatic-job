"""
Full Automated Pipeline:
1. Auto-fetches 200 tech companies & active hiring contacts
2. Validates live domains
3. Generates tailored applications for Karthik Raja L
4. Sends emails with attachments via Gmail SMTP safely (respecting daily limits & delays)
"""

import sys
import argparse
from fetch_companies import generate_leads
from email_bot import send_batch

def run_pipeline(count=200, role="Technical Project Manager", dry_run=False):
    print("=" * 60)
    print(f"🚀 STARTING COMPLETE AUTOMATED JOB OUTREACH PIPELINE")
    print(f"🎯 Target: {count} Companies | Role: {role}")
    print(f"⚙️ Mode: {'DRY RUN (Simulation)' if dry_run else 'LIVE SENDING'}")
    print("=" * 60)

    # Step 1: Auto-fetch fresh companies and generate leads.csv
    print("\n[STEP 1/2] Discovering & verifying active companies...")
    fetched_count = generate_leads(target_count=count, default_role=role)

    if fetched_count == 0:
        print("❌ No leads were fetched. Aborting.")
        sys.exit(1)

    # Step 2: Send outreach batch
    print(f"\n[STEP 2/2] Initiating email outreach to {fetched_count} companies...")
    send_batch(dry_run=dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-End Automated Company Lead Fetching & Outreach Pipeline")
    parser.add_argument("--count", type=int, default=200, help="Number of companies to target (default: 200)")
    parser.add_argument("--role", type=str, default="Technical Project Manager", help="Target Job Role")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without sending emails")
    args = parser.parse_args()

    run_pipeline(count=args.count, role=args.role, dry_run=args.dry_run)
