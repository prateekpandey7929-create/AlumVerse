from django.shortcuts import render
from accounts.models import User
from accounts.models import Profile


def alumni_directory(request):
    alumni = User.objects.filter(role='alumni')
    return render(request, 'alumni_directory.html', {'alumni': alumni})


def alumni_profile(request, id):
    profile = Profile.objects.get(user_id=id)
    return render(request, 'alumni_profile.html', {'profile': profile})


def alumni_search(request):
    batch = request.GET.get("batch")
    dept = request.GET.get("dept")
    skill = request.GET.get("skill")

    alumni = Profile.objects.all()

    if batch:
        alumni = alumni.filter(user__graduation_year=batch)

    if dept:
        alumni = alumni.filter(user__branch__icontains=dept)

    if skill:
        alumni = alumni.filter(skills__icontains=skill)

    return render(request, "alumni_search.html", {"alumni": alumni})
