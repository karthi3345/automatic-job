"""
Generates Karthik Raja L's professional PDF resume.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUT_PATH_STATIC = os.path.join(os.path.dirname(__file__), "job_agent", "static", "job_agent", "Karthik_Raja_Resume.pdf")
OUT_PATH_BOT = os.path.join(os.path.dirname(__file__), "job_outreach_bot", "resume.pdf")

def generate_pdf():
    doc = SimpleDocTemplate(
        OUT_PATH_STATIC,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0284c7'),
        fontName='Helvetica-Bold',
        spaceAfter=4
    )
    contact_style = ParagraphStyle(
        'DocContact',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )
    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2
    )
    role_title_style = ParagraphStyle(
        'RoleTitle',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f172a')
    )

    story = []

    # Header
    story.append(Paragraph("KARTHIK RAJA L", title_style))
    story.append(Paragraph("Technical Project Coordinator / Technical Project Manager", subtitle_style))
    story.append(Paragraph("📧 lkarthikaraja@gmail.com &nbsp;|&nbsp; 📞 +91 8610177637 &nbsp;|&nbsp; 🔗 GitHub: https://github.com/karthi3345 &nbsp;|&nbsp; 🌐 Portfolio: https://dashing-praline-9e34ab.netlify.app/", contact_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=6))

    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
    summary_text = (
        "Highly accomplished <b>Technical Project Coordinator / Project Manager with 4+ years of experience</b> "
        "driving end-to-end delivery of complex software, AI, data, banking, gaming, healthcare, and IoT enterprise platforms. "
        "Expert in translating business requirements into technically executable plans, coordinating engineering teams across frontend, "
        "backend, AI/ML, cloud, and QA functions. Strong ownership of Agile delivery, sprint execution, release management, and stakeholder governance."
    )
    story.append(Paragraph(summary_text, body_style))

    # Core Skills
    story.append(Paragraph("CORE SKILLS & TECHNOLOGIES", section_style))
    skills_text = (
        "<b>Project Management:</b> Agile Scrum, SAFe (Foundational), Waterfall, Full-Cycle SDLC, Sprint & Release Planning, Milestone & Roadmap Management, RAID Logs, Production Release Management, Stakeholder Coordination.<br/>"
        "<b>Technical & Architecture:</b> Python (Django, DRF), REST APIs, SQL (PostgreSQL, MySQL), React.js, Node.js, Microservices Architecture review, AWS (EC2, S3), CI/CD Pipelines (GitHub Actions/Jenkins).<br/>"
        "<b>AI / Advanced Analytics:</b> Machine Learning concepts, Time-Series Forecasting (RNN Models), Data Pipelines, Feature Engineering, Model Validation Metrics.<br/>"
        "<b>Tools:</b> JIRA, Confluence, Trello, GitHub, Postman, Power BI, Figma (UI/UX Review)."
    )
    story.append(Paragraph(skills_text, body_style))

    # Professional Experience
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_style))

    # Job 1
    story.append(Paragraph("<b>IT Project Coordinator – Gaming, Banking & AI Projects</b> | HandledTech Labs &nbsp;&nbsp;<i>(Feb 2025 – Present)</i>", role_title_style))
    story.append(Paragraph("• <b>AI-Based Stock Prediction System:</b> Coordinated end-to-end lifecycle across AI/ML engineers, Django backend (Python, DRF, PostgreSQL), React frontend, and QA. Monitored RNN-based prediction models, validated backend contracts, and ensured market data pipeline integrity.", bullet_style))
    story.append(Paragraph("• <b>Banking & Financial Services Application:</b> Managed KYC workflows (verification, approvals), merchant management, RBAC access control, UAT sign-offs, and production readiness under strict compliance.", bullet_style))
    story.append(Paragraph("• <b>Casino Gaming & Sportsbook Platform:</b> Owned sprint execution from requirements to production deployment. Led daily Scrums, burn-down tracking in JIRA, and post-release incident triage.", bullet_style))

    # Job 2
    story.append(Paragraph("<b>PMO Analyst</b> | KatalTech &nbsp;&nbsp;<i>(Apr 2022 – Jan 2025)</i>", role_title_style))
    story.append(Paragraph("• <b>Air Quality Monitoring Control System (IoT):</b> Managed full lifecycle across Flutter, Embedded C, and MQTT teams; tracked milestones and oversaw real-time dashboard deployments.", bullet_style))
    story.append(Paragraph("• <b>Healthcare Web & Mobile Application:</b> Gathered clinical requirements, led walkthrough workshops, and coordinated QA testing and UAT adoption.", bullet_style))
    story.append(Paragraph("• <b>PMO HRMS Enterprise Portal:</b> Led governance, sprint roadmaps, and stakeholder alignment across HR, Finance, and IT for employee lifecycle management.", bullet_style))

    # Education & Certifications
    story.append(Paragraph("EDUCATION & CERTIFICATIONS", section_style))
    story.append(Paragraph("• <b>Bachelor of Engineering (BE)</b> – Velammal College of Engineering and Technology", bullet_style))
    story.append(Paragraph("• <b>Certifications:</b> Project Management (Udemy) &nbsp;|&nbsp; Django Framework (Udemy) &nbsp;|&nbsp; Software Testing (Greens Technology)", bullet_style))

    doc.build(story)
    print(f"Generated {OUT_PATH_STATIC}")

    # Copy to bot directory as well
    import shutil
    shutil.copyfile(OUT_PATH_STATIC, OUT_PATH_BOT)
    print(f"Copied to {OUT_PATH_BOT}")

if __name__ == "__main__":
    generate_pdf()
