from django.shortcuts import render
from django.db.models import Q
from accounts.models import User
from accounts.models import Profile


def alumni_directory(request):
    alumni = User.objects.filter(role='alumni')
    return render(request, 'alumni_directory.html', {'alumni': alumni})


def alumni_profile(request, id):
    profile = Profile.objects.get(user_id=id)
    return render(request, 'alumni_profile.html', {'profile': profile})


def alumni_search(request):
    q = request.GET.get("q", "").strip()
    batch = request.GET.get("batch", "").strip()
    dept = request.GET.get("dept", "").strip()

    # Filter profiles of users who are verified alumni
    alumni = Profile.objects.filter(user__role='alumni')

    if q:
        alumni = alumni.filter(
            Q(user__full_name__icontains=q) |
            Q(user__username__icontains=q) |
            Q(skills__icontains=q) |
            Q(company__icontains=q)
        ).distinct()

    if batch:
        alumni = alumni.filter(user__graduation_year=batch)

    if dept:
        alumni = alumni.filter(user__branch__icontains=dept)

    return render(request, "alumni_search.html", {"alumni": alumni})
