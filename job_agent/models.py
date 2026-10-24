from django.db import models

class JobLead(models.Model):
    company_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    apply_url = models.URLField(max_length=500, blank=True, null=True)
    source = models.CharField(max_length=100, default='Curated Tech Directory')
    location = models.CharField(max_length=100, default='Remote / Hybrid')
    status = models.CharField(max_length=50, default='NEW')  # NEW, EMAILED, APPLIED
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name} - {self.role}"


class SentApplication(models.Model):
    recipient_email = models.CharField(max_length=255, unique=True)
    company_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    sent_date = models.DateField(auto_now_add=True)
    sent_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='SENT')

    class Meta:
        ordering = ['-sent_timestamp']

    def __str__(self):
        return f"{self.company_name} - {self.recipient_email} ({self.status})"
