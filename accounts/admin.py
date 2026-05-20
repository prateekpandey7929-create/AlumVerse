from django.contrib import admin
from .models import User, Profile, Notification
from .models import AlumniRequest

# Register your models here.

admin.site.register(AlumniRequest)
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Notification)