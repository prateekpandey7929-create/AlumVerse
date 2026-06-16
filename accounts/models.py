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
    full_name = models.CharField(max_length=200, blank=True, null=True)
    enrollment_no = models.CharField(max_length=50, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    admission_year = models.IntegerField(blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        current_year = datetime.now().year

        if self.graduation_year and current_year >= self.graduation_year:
            self.role = "alumni"

        if self.email:
            self.email = self.email.strip().lower()

        if self.personal_email:
            self.personal_email = self.personal_email.strip().lower()
        else:
            self.personal_email = None

        if not self.username and self.email:
            self.username = self.email.split('@')[0]

        if self.username:
            prefix = self.username
            username = prefix
            count = 1
            # Import dynamically to avoid circular references
            from accounts.models import User as UserModel
            
            qs = UserModel.objects.filter(username=username)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
                
            while qs.exists():
                username = f"{prefix}{count}"
                count += 1
                qs = UserModel.objects.filter(username=username)
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
            self.username = username

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

    @property
    def profile_photo_url(self):
        if self.profile_photo and hasattr(self.profile_photo, 'url'):
            try:
                return self.profile_photo.url
            except ValueError:
                pass
        return '/static/images/profile.png'



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


class Post(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'General Tech Discussion'),
        ('job_alert', 'Job / Placement Alert'),
        ('internship', 'Internship Update'),
        ('motivation', 'Career Motivation'),
        ('hackathon', 'Hackathon / Event'),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.category} ({self.created_at.strftime('%Y-%m-%d')})"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')

    def __str__(self):
        return f"Image for Post {self.post.id}"


