from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
from .recommendation import recommend_alumni
from .skill_gap import analyze_skill_gap
from django.contrib.auth.decorators import login_required
from .resume_analyzer import analyze_resume
from .career_path import recommend_career



@login_required
def career_path(request):
    skills = request.user.profile.skills or ""
    career = recommend_career(skills)
    return render(request, "career_path.html", {"career": career})


import pdfplumber
from django.contrib import messages

@login_required
def resume_analyzer(request):
    score = None
    missing = []

    if request.method == "POST":

        file = request.FILES.get("resume")

        if not file:
            messages.error(request, "Please upload a file")
            return redirect("/resume-analyzer/")

        # ✅ Check file type
        if not file.name.endswith(".pdf"):
            messages.error(request, "Only PDF files are allowed")
            return redirect("/resume-analyzer/")

        try:
            text = ""

            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

            from .resume_analyzer import analyze_resume as analyze_resume_function
            score, missing = analyze_resume_function(file)

        except Exception:
            messages.error(request, "Invalid or corrupted PDF file")
            return redirect("/resume-analyzer/")

    return render(request, "resume_analyzer.html", {
        "score": score,
        "missing": missing
    })



@login_required
def skill_gap(request):
    result = []

    if request.method == "POST":

        career = request.POST.get("career")

        skills = request.user.profile.skills or ""

        result = analyze_skill_gap(skills, career)

    return render(request, "skill_gap.html", {"result": result})


@login_required
def alumni_recommendations(request):

    student_profile = request.user.profile
    # Get recommended alumni IDs
    recommended_ids = recommend_alumni(student_profile)
    # Fetch alumni profiles
    alumni_profiles = Profile.objects.filter(user_id__in=recommended_ids)
    context = {
        "alumni": alumni_profiles
    }
    return render(request, "ai_recommendations.html", context)

from django.shortcuts import redirect
from .chatbot import chatbot_response

def chatbot(request):
    if request.method == "POST":

        query = request.POST.get("query")

        response = chatbot_response(query)

        request.session["chatbot_response"] = response

    return redirect(request.META.get("HTTP_REFERER", "/"))
