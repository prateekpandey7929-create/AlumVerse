from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import OpportunityForm
from .models import Opportunity
from accounts.models import Notification
from accounts.models import User

@login_required
def post_opportunity(request):
    if request.method == "POST":

        form = OpportunityForm(request.POST)

        if form.is_valid():

            opportunity = form.save(commit=False)

            opportunity.posted_by = request.user

            opportunity.save()

            students = User.objects.filter(role='student')

            for student in students:
                Notification.objects.create(
                user=student,
                message=f"New {opportunity.type} posted: {opportunity.title}"
            )

            return redirect('/jobs/')

    else:

        form = OpportunityForm()

    return render(request, 'post_opportunity.html', {'form': form})

def job_list(request):
    opportunities = Opportunity.objects.all().order_by('-created_at')
    return render(request, 'jobs.html', {'opportunities': opportunities})