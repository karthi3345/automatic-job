# 🚀 End-to-End Automated Job Application Agent

This agent **automatically fetches real companies**, discovers their hiring mailboxes, personalizes the application for **Karthik Raja L**, and sends up to **200 emails per day completely free of cost** using Gmail.

---

## ⚡ How It Works (Fully Autonomous)

```
[1. Auto-Fetch] ──> Connects to 1,100+ verified tech company directories & RemoteOK API
         │
[2. Domain & Mail Verification] ──> Verifies live DNS and builds careers@{company}.com
         │
[3. Custom Pitch Generation] ──> Formats cover letter using Karthik's 4+ yrs PM experience
         │
[4. Attachment & Dispatch] ──> Attaches resume.pdf & sends via Gmail SMTP with anti-spam jitter
         │
[5. Local SQLite Database] ──> Records sent emails in sent_history.db (prevents duplicate emails)
```

---

## ⚙️ Initial Setup (1 Time Only)

### 1. Gmail App Password (Free)
1. Go to your Google Account: [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Turn **2-Step Verification** ON.
3. Open [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Generate an App Password named `Job Agent` and copy the 16 characters.
5. In [`job_outreach_bot/.env`](file:///d:/myvepower-django/job_outreach_bot/.env), paste it:
   ```ini
   SENDER_APP_PASSWORD=abcd efgh ijkl mnop
   ```

### 2. Put your Resume
Save your resume PDF as:
`d:/myvepower-django/job_outreach_bot/resume.pdf`

---

## 🏃 Run The Full Automation

### Option A: Run 1-Click Complete Pipeline (Fetch + Send 200 Emails)
```powershell
.\venv\Scripts\python.exe job_outreach_bot/run_automation.py --count 200 --role "Technical Project Manager"
```

### Option B: Dry Run Simulation (Test without sending real emails)
```powershell
.\venv\Scripts\python.exe job_outreach_bot/run_automation.py --count 200 --role "Technical Project Manager" --dry-run
```

### Option C: Only Fetch Fresh Companies to `leads.csv`
```powershell
.\venv\Scripts\python.exe job_outreach_bot/fetch_companies.py --count 200 --role "Technical Project Manager"
```

---

## 🛡️ Anti-Spam Safety Controls
- **200 Daily Cap**: Stops automatically once the quota is reached.
- **Random 25–60s Jitter**: Spreads out email sending so Google does not flag your activity.
- **Deduplication**: `sent_history.db` guarantees you will never email the same company twice.
