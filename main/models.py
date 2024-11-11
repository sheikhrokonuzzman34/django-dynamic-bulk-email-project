from django.db import models

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EmailLog(models.Model):
    subject = models.CharField(max_length=200)
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=100)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed')
    ])
    error_message = models.TextField(null=True, blank=True)
