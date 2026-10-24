from django.db import models

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
