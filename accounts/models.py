from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):


    ROLE_CHOICES = (
        ('student', 'Student'),
        ('alumni', 'Alumni'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    branch = models.CharField(max_length=100, blank=True, null=True)
    admission_year = models.IntegerField(blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):

        current_year = datetime.now().year

        if self.graduation_year and current_year >= self.graduation_year:
            self.role = "alumni"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    bio = models.TextField(blank=True)

    skills = models.TextField(blank=True)

    projects = models.TextField(blank=True)

    achievements = models.TextField(blank=True)

    linkedin = models.URLField(blank=True)

    github = models.URLField(blank=True)

    portfolio = models.URLField(blank=True)

    company = models.CharField(max_length=200, blank=True)

    job_role = models.CharField(max_length=200, blank=True)

    experience = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message



class AlumniRequest(models.Model):

    name = models.CharField(max_length=100)

    email = models.EmailField()

    scholar_no = models.CharField(max_length=50)

    branch = models.CharField(max_length=100)

    graduation_year = models.IntegerField()

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name
