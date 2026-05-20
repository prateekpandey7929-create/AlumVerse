from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL
class Opportunity(models.Model):
    TYPE_CHOICES = (
        ('job', 'Job'),
        ('internship', 'Internship'),
        ('event', 'Event'),
    )

    title = models.CharField(max_length=200)

    company = models.CharField(max_length=200)

    description = models.TextField()

    location = models.CharField(max_length=200)

    deadline = models.DateField()

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
