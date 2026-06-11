import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, AlumniRequest
from datetime import datetime

# ===============================

# 1️⃣ REGISTER FORM (WITH VALIDATION)

# ===============================

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'full_name',
            'email',
            'enrollment_no',
            'branch',
            'admission_year',
            'graduation_year',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_enrollment_no(self):
        enrollment_no = self.cleaned_data.get("enrollment_no")
        if not enrollment_no:
            raise forms.ValidationError("Enrollment number is required")
        if not enrollment_no.startswith("0818"):
            raise forms.ValidationError("Enrollment number must start with 0818")
        return enrollment_no

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Email is required")
        if not email.endswith("@indoreinstitute.com"):
            raise forms.ValidationError("Email must end with @indoreinstitute.com")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists")
        return email

    def clean_graduation_year(self):
        graduation_year = self.cleaned_data.get("graduation_year")
        current_year = datetime.now().year
        if graduation_year and graduation_year < current_year:
            raise forms.ValidationError("Graduation year cannot be in the past.")
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

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match")
        return cleaned_data

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

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


# ===============================

# 4️⃣ PERSONAL EMAIL FORM

# ===============================

class PersonalEmailForm(forms.Form):
    personal_email = forms.EmailField(
        label="Personal Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your personal email (e.g. gmail)'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_personal_email(self):
        email = self.cleaned_data.get("personal_email")
        if not email:
            raise forms.ValidationError("Email is required")
        email = email.strip().lower()
        if email.endswith("@indoreinstitute.com"):
            raise forms.ValidationError("Please enter a personal email address (e.g. Gmail, Outlook), not the college email")
        
        # Check if the email is already in use by another user's primary or secondary email
        qs1 = User.objects.filter(email=email)
        qs2 = User.objects.filter(personal_email=email)
        
        if self.user:
            qs1 = qs1.exclude(id=self.user.id)
            qs2 = qs2.exclude(id=self.user.id)
            
        if qs1.exists() or qs2.exists():
            raise forms.ValidationError("This email address is already in use by another user")
            
        return email


# ===============================

# 5️⃣ ADMIN USER FORM (FOR USER CRUD)

# ===============================

class AdminUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        required=False,
        help_text="Required for new users. Leave blank for existing users to keep current password."
    )

    class Meta:
        model = User
        fields = [
            'full_name',
            'email',
            'enrollment_no',
            'branch',
            'admission_year',
            'graduation_year',
            'role',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        # If this is a new user (no self.instance.pk), password is required
        if not self.instance.pk and not password:
            self.add_error('password', "Password is required for new users")
        return cleaned_data
