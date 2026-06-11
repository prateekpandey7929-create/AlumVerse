from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
from .recommendation import recommend_alumni
from .skill_gap import analyze_skill_gap
from .resume_analyzer import analyze_resume
from .career_path import recommend_career
from django.contrib import messages

@login_required
def career_path(request):
    """
    Recommends career paths based on user skills, and queries matching 
    placements/jobs from the database.
    """
    skills = request.user.profile.skills or ""
    careers = recommend_career(skills)
    
    # Query job opportunities matching recommended career paths
    from jobs.models import Opportunity
    from django.db.models import Q
    
    matching_jobs = []
    if careers:
        query = Q()
        for c in careers:
            query |= Q(title__icontains=c) | Q(description__icontains=c)
        matching_jobs = Opportunity.objects.filter(query).order_by("-created_at")[:5]
        
    return render(request, "career_path.html", {
        "career": careers,
        "matching_jobs": matching_jobs
    })

@login_required
def resume_analyzer(request):
    """
    Analyzes uploaded PDF resume against a selected target career track,
    returning ATS score, missing items, found items, and layout advice.
    """
    score = None
    missing = []
    found = []
    advice = []
    selected_career = "Backend Developer"

    if request.method == "POST":
        file = request.FILES.get("resume")
        selected_career = request.POST.get("career", "Backend Developer")

        if not file:
            messages.error(request, "Please upload a resume file")
            return redirect("/resume-analyzer/")

        if not file.name.endswith(".pdf"):
            messages.error(request, "Only PDF format documents are supported")
            return redirect("/resume-analyzer/")

        try:
            from .resume_analyzer import analyze_resume as analyze_resume_function
            score, missing, found, advice = analyze_resume_function(file, selected_career)
        except Exception as e:
            print(f"Error during resume analysis: {e}")
            messages.error(request, "Invalid or corrupted PDF file uploaded")
            return redirect("/resume-analyzer/")

    return render(request, "resume_analyzer.html", {
        "score": score,
        "missing": missing,
        "found": found,
        "advice": advice,
        "selected_career": selected_career
    })

@login_required
def skill_gap(request):
    """
    Calculates technical skill gaps relative to the chosen career path.
    """
    result = []
    selected_career = "Backend Developer"
    
    if request.method == "POST":
        selected_career = request.POST.get("career", "Backend Developer")
        skills = request.user.profile.skills or ""
        result = analyze_skill_gap(skills, selected_career)

    return render(request, "skill_gap.html", {
        "result": result,
        "selected_career": selected_career
    })

@login_required
def alumni_recommendations(request):
    """
    Suggests compatible alumni mentors using TF-IDF cosine similarity vector checks.
    """
    student_profile = request.user.profile
    recommended_ids = recommend_alumni(student_profile)
    alumni_profiles = Profile.objects.filter(user_id__in=recommended_ids)
    
    return render(request, "ai_recommendations.html", {
        "alumni": alumni_profiles
    })

from .chatbot import chatbot_response

def chatbot(request):
    """
    Receives user chatbot query posts and returns JSON response.
    """
    if request.method == "POST":
        query = request.POST.get("query")
        response = chatbot_response(query)
        return JsonResponse({"response": response})
    return JsonResponse({"error": "Invalid request"}, status=400)
