import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, AlumniRequest
from datetime import datetime

# ===============================

# 1️⃣ REGISTER FORM (WITH VALIDATION)

# ===============================

class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'branch',
            'admission_year',
            'graduation_year',
            'password1',
            'password2'
        ]

    def clean_graduation_year(self):
        graduation_year = self.cleaned_data.get("graduation_year")

        current_year = datetime.now().year

        # Prevent alumni registration from website
        if graduation_year < current_year:

            raise forms.ValidationError(
                "Graduation year cannot be in the past."
            )

        return graduation_year

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters")

        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Password must contain at least 1 uppercase letter")

        if not re.search(r"[a-z]", password):
            raise forms.ValidationError("Password must contain at least 1 lowercase letter")

        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least 1 digit")

        if not re.search(r"[!@#$%^&*]", password):
            raise forms.ValidationError("Password must contain at least 1 special character")

        return password

# ===============================

# 2️⃣ PROFILE FORM

# ===============================

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            'profile_photo',
            'bio',
            'skills',
            'projects',
            'achievements',
            'linkedin',
            'github',
            'portfolio',
            'company',
            'job_role',
            'experience'
        ]

# ===============================

# 3️⃣ ALUMNI REQUEST FORM

# ===============================

class AlumniRequestForm(forms.ModelForm):

    class Meta:
        model = AlumniRequest
        fields = [
            'name',
            'email',
            'scholar_no',
            'branch',
            'graduation_year'
        ]
