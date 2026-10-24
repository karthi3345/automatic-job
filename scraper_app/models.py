from django.db import models

class Provider(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Game(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='games')
    name = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=500, blank=True, null=True)
    ocr_stats = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider.name} - {self.name}"
