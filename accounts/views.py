from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm, ProfileForm, AlumniRequestForm
from .models import Profile, Notification

from jobs.models import Opportunity
from messaging.models import Message

# =========================================

# REGISTER VIEW

# =========================================

def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # Only student registration allowed
            user.role = "student"

            user.save()

            messages.success(
                request,
                "Registration successful! Please login."
            )

            return redirect('/login/')

        else:

            messages.error(
                request,
                "Please correct the errors below"
            )

    else:

        form = RegisterForm()

    return render(
        request,
        'register.html',
        {'form': form}
    )

# =========================================

# LOGIN VIEW

# =========================================

def user_login(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # WRONG CREDENTIALS

        if user is None:

            messages.error(
                request,
                "Invalid email or password"
            )

            return redirect('/login/')

        # ADMIN LOGIN

        if role == "admin":

            if user.is_staff:

                login(request, user)

                return redirect('/admin/')

            else:

                messages.error(
                    request,
                    "You are not authorized as Admin"
                )

                return redirect('/login/')

        # STUDENT LOGIN

        elif role == "student":

            if user.role == "student":

                login(request, user)

                return redirect('/dashboard/')

            else:

                messages.error(
                    request,
                    "Student account not found"
                )

                return redirect('/login/')

        # ALUMNI LOGIN

        elif role == "alumni":

            if user.role == "alumni":

                login(request, user)

                return redirect('/dashboard/')

            else:

                messages.error(
                    request,
                    "Alumni account not found"
                )

                return redirect('/login/')

    return render(request, "login.html")


# =========================================

# DASHBOARD VIEW

# =========================================

@login_required
def dashboard(request):
    if request.user.role == "student":

        return render(
            request,
            'dashboard/student_dashboard.html'
        )

    elif request.user.role == "alumni":

        return render(
            request,
            'dashboard/alumni_dashboard.html'
        )

    else:

        return redirect('/')

# =========================================

# PROFILE VIEW

# =========================================

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        'profile.html',
        {'profile': profile}
    )

# =========================================

# EDIT PROFILE VIEW

# =========================================

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully"
            )

            return redirect('/profile/')

    else:

        form = ProfileForm(instance=profile)

    return render(
        request,
        'edit_profile.html',
        {'form': form}
    )

# =========================================

# NOTIFICATIONS VIEW

# =========================================

@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return render(
        request,
        'notifications.html',
        {'notifications': notifications}
    )


# =========================================

# LOGOUT VIEW

# =========================================

def user_logout(request):
    logout(request)

    messages.success(
        request,
        "Logged out successfully"
    )

    return redirect('/')

# =========================================

# ALUMNI REQUEST VIEW

# =========================================

def alumni_request(request):
    if request.method == "POST":

        form = AlumniRequestForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your alumni request has been submitted successfully"
            )

            return redirect('/')

        else:

            messages.error(
                request,
                "Please correct the errors below"
            )

    else:

        form = AlumniRequestForm()

    return render(
        request,
        "alumni_request.html",
        {"form": form}
    )