from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Notification, AlumniRequest


class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "role",
                    "branch",
                    "admission_year",
                    "graduation_year",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "role",
                    "branch",
                    "admission_year",
                    "graduation_year",
                )
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(Notification)
admin.site.register(AlumniRequest)