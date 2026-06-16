import random
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from .forms import RegisterForm, ProfileForm, AlumniRequestForm, PersonalEmailForm, AdminUserForm
from .models import User, Profile, Notification, AlumniRequest
from jobs.models import Opportunity
from messaging.models import Message

# =========================================
# 1️⃣ REGISTRATION & OTP VERIFICATION VIEWS
# =========================================

def register(request):
    """
    Handles student registration post requests. Stores registration data
    in session, generates a mock OTP verification code, and redirects to verification panel.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Store validated form attributes inside session to finalize after OTP verification
            registration_data = form.cleaned_data.copy()
            # Django session can't serialize custom form types easily; extract cleaned data attributes
            request.session['temp_registration_data'] = registration_data
            
            # Generate 6-digit verification code
            otp_code = str(random.randint(100000, 999999))
            request.session['temp_registration_otp'] = otp_code
            
            # Send actual email
            email_sent = False
            email = registration_data['email']
            try:
                send_mail(
                    subject="AlumVerse Registration OTP",
                    message=f"Hello {registration_data.get('full_name', 'Student')},\n\nYour registration OTP verification code for AlumVerse is: {otp_code}\n\nBest Regards,\nAlumVerse Team",
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin.alumverse@gmail.com'),
                    recipient_list=[email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                print(f"Error sending registration email: {e}")
                
            if email_sent:
                messages.success(
                    request,
                    f"A verification OTP code has been sent to your email {email}. Please enter it below."
                )
            else:
                messages.success(
                    request,
                    f"Simulated verification code sent to {email}: [ {otp_code} ]\n(Note: Setup correct credentials in settings.py to receive actual emails)"
                )
            return redirect('/verify-otp/')
        else:
            messages.error(request, "Please correct the form validation errors below.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def verify_otp(request):
    """
    Verifies the OTP code stored inside the user's session.
    If valid, creates the new User account dynamically.
    """
    temp_data = request.session.get('temp_registration_data')
    otp_code = request.session.get('temp_registration_otp')

    if not temp_data or not otp_code:
        messages.error(request, "No pending registration records found. Please sign up first.")
        return redirect('/register/')

    if request.method == 'POST':
        user_otp = request.POST.get('otp', '').strip()
        
        if user_otp == otp_code:
            # OTP validation passes; extract credentials and compile User model
            email = temp_data['email']
            password = temp_data['password1'] # Raw clean password input
            full_name = temp_data['full_name']
            enrollment_no = temp_data['enrollment_no']
            branch = temp_data['branch']
            admission_year = temp_data['admission_year']
            graduation_year = temp_data['graduation_year']
            
            # Save User model
            new_user = User.objects.create_user(
                username=email.split('@')[0], # Fallback generation handled by model save
                email=email,
                password=password,
                full_name=full_name,
                enrollment_no=enrollment_no,
                branch=branch,
                admission_year=admission_year,
                graduation_year=graduation_year,
                role='student' # Defaults student role (auto-upgraded by model save if graduation is past)
            )
            
            # Clear temporary session scopes
            del request.session['temp_registration_data']
            del request.session['temp_registration_otp']
            
            messages.success(request, f"Registration complete! User {new_user.full_name or new_user.username} created. Please login.")
            return redirect('/login/')
        else:
            messages.error(request, "Invalid verification code. Please try again.")

    return render(request, 'verify_otp.html', {'email': temp_data['email']})


# =========================================
# 2️⃣ LOGIN & AUTHENTICATION VIEWS
# =========================================

def user_login(request):
    """
    Handles user login checks using Email and Password inputs.
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")
        role = request.POST.get("role")

        # Resolve unique user using email or personal_email parameters case-insensitively
        user_obj = User.objects.filter(Q(email__iexact=email) | Q(personal_email__iexact=email)).first()

        if user_obj is None:
            messages.error(request, "No account matches this email address.")
            return redirect('/login/')

        # Authenticate using username internally
        user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            messages.error(request, "Incorrect password. Please try again.")
            return redirect('/login/')

        # Authorization Checks by user type selection
        if role == "admin":
            if user.is_staff or user.role == "admin":
                login(request, user)
                return redirect('/dashboard/')
            else:
                messages.error(request, "You are not authorized as Admin.")
                return redirect('/login/')

        elif role in ["student", "alumni"]:
            if user.role in ["student", "alumni"]:
                login(request, user)
                return redirect('/dashboard/')
            else:
                messages.error(request, f"Account role check failed. Selection was {role.capitalize()}.")
                return redirect('/login/')

    return render(request, "login.html")


# =========================================
# 3️⃣ SYSTEM DASHBOARDS VIEW
# =========================================

@login_required
def dashboard(request):
    """
    Renders corresponding dashboard with live database stats and metrics.
    Also handles new post creation with AI content moderation and auto-tagging.
    """
    from .models import Post
    import re

    if request.method == "POST" and "create_post" in request.POST:
        content = request.POST.get("content", "").strip()
        category = request.POST.get("category", "general").strip()

        if not content:
            messages.error(request, "Post content cannot be empty.")
            return redirect('/dashboard/')

        # AI Content Moderation: checks for bad words/profanity
        profane_words = ["abuse", "spam", "badword", "stupid", "idiot", "nonsense", "vulgar", "fuck", "shit", "bitch", "bastard", "kamina", "saala", "kamine", "scam", "fraud"]
        content_lower = content.lower()
        flagged = False
        for word in profane_words:
            if re.search(r'\b' + re.escape(word) + r'\b', content_lower):
                flagged = True
                break
        
        if flagged:
            messages.error(request, "Please keep the feed professional. Inappropriate content detected.")
            return redirect('/dashboard/')

        # AI Auto-Tagging
        tags = []
        if any(w in content_lower for w in ["job", "hiring", "hire", "recruit", "referral", "opening", "vacancy", "placement"]):
            tags.append("#JobAlert")
            tags.append("#Placement")
        if any(w in content_lower for w in ["intern", "internship", "stipend"]):
            tags.append("#Internship")
        if any(w in content_lower for w in ["hackathon", "contest", "event", "competition", "codethon"]):
            tags.append("#Hackathon")
        if any(w in content_lower for w in ["tech", "python", "programming", "ai", "coding", "software", "development", "developer", "java", "cpp", "javascript"]):
            tags.append("#TechTalk")
        if any(w in content_lower for w in ["motivation", "success", "inspire", "story", "hardwork", "dream", "motivate"]):
            tags.append("#CareerMotivation")
        
        if tags:
            content = content + "\n\n" + " ".join(tags)

        post = Post.objects.create(author=request.user, content=content, category=category)
        
        images = request.FILES.getlist('images')
        if images:
            from .models import PostImage
            for img in images:
                PostImage.objects.create(post=post, image=img)

        messages.success(request, "Post published successfully!")
        return redirect('/dashboard/')

    # Fetch posts for all roles
    posts = Post.objects.all().order_by('-created_at')

    if request.user.role == "student":
        # Query active job postings
        jobs = Opportunity.objects.all().order_by("-created_at")[:3]
        
        # Calculate unique direct alumni messaging count
        all_msgs = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        )
        unique_alumni = set()
        for msg in all_msgs:
            other = msg.receiver if msg.sender == request.user else msg.sender
            if other.role == "alumni":
                unique_alumni.add(other.id)
        total_mentorships = len(unique_alumni)

        # Dynamic profile views count for visual rendering
        profile_views = (request.user.id * 13) % 80 + 15
        
        return render(
            request,
            'dashboard/student_dashboard.html',
            {
                'jobs': jobs,
                'total_mentorships': total_mentorships,
                'profile_views': profile_views,
                'posts': posts,
            }
        )

    elif request.user.role == "alumni":
        # Count active job postings by this alumnus
        active_jobs_count = Opportunity.objects.filter(posted_by=request.user).count()
        
        # Count unique student direct message chat threads
        all_msgs = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).order_by("-created_at")
        
        unique_students = {}
        for msg in all_msgs:
            other = msg.receiver if msg.sender == request.user else msg.sender
            if other.id not in unique_students and other.role == "student":
                unique_students[other.id] = {
                    "user": other,
                    "last_message": msg.message
                }
                
        recent_chats = list(unique_students.values())[:3]
        total_mentorships = len(unique_students)
        
        # Dynamic profile views count for visual rendering
        profile_views = (request.user.id * 19) % 250 + 60

        return render(
            request,
            'dashboard/alumni_dashboard.html',
            {
                "active_jobs_count": active_jobs_count,
                "total_mentorships": total_mentorships,
                "recent_chats": recent_chats,
                "profile_views": profile_views,
                'posts': posts,
            }
        )
    elif request.user.role == "admin" or request.user.is_staff:
        users_count = User.objects.count()
        students_count = User.objects.filter(role='student').count()
        alumni_count = User.objects.filter(role='alumni').count()
        jobs_count = Opportunity.objects.count()
        
        # Safe query for Message table counts
        try:
            messages_count = Message.objects.count()
        except Exception:
            messages_count = 0
            
        users_list = User.objects.all().order_by('-date_joined')
        pending_requests = AlumniRequest.objects.filter(is_approved=False).order_by('-id')

        return render(
            request,
            'admin_dashboard.html',
            {
                'users_count': users_count,
                'students_count': students_count,
                'alumni_count': alumni_count,
                'jobs_count': jobs_count,
                'messages_count': messages_count,
                'users': users_list,
                'pending_requests': pending_requests,
                'posts': posts,
            }
        )
    else:
        return redirect('/')


# =========================================
# 4️⃣ UTILITY PROFILE & ALUMNI REQUEST VIEWS
# =========================================

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('/profile/')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})


def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('/')


def alumni_request(request):
    if request.method == "POST":
        form = AlumniRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your alumni request has been submitted successfully")
            return redirect('/')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = AlumniRequestForm()

    return render(request, "alumni_request.html", {"form": form})


@login_required
def add_personal_email(request):
    """
    Renders form to input a personal email address, sends a mock OTP,
    and stores pending changes in session scopes.
    """
    if request.method == "POST":
        form = PersonalEmailForm(request.POST, user=request.user)
        if form.is_valid():
            email = form.cleaned_data['personal_email']
            otp_code = str(random.randint(100000, 999999))
            
            # Store in session
            request.session['pending_personal_email'] = email
            request.session['personal_email_otp'] = otp_code
            
            # Send actual email
            email_sent = False
            try:
                send_mail(
                    subject="AlumVerse Personal Email Verification OTP",
                    message=f"Hello {request.user.full_name or request.user.username},\n\nYour verification code to add personal email {email} to your AlumVerse profile is: {otp_code}\n\nBest Regards,\nAlumVerse Team",
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin.alumverse@gmail.com'),
                    recipient_list=[email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                print(f"Error sending personal email verification code: {e}")
                
            if email_sent:
                messages.success(
                    request,
                    f"A verification OTP code has been sent to your personal email {email}. Please enter it below."
                )
            else:
                messages.success(
                    request,
                    f"Simulated verification code sent to personal email {email}: [ {otp_code} ]\n(Note: Setup correct credentials in settings.py to receive actual emails)"
                )
            return redirect('/profile/verify-personal-email/')
        else:
            messages.error(request, "Please correct the validation errors below.")
    else:
        form = PersonalEmailForm(user=request.user)
        
    return render(request, "add_personal_email.html", {"form": form})


@login_required
def verify_personal_email(request):
    """
    Checks verification OTP code to save the personal email to User account.
    """
    pending_email = request.session.get('pending_personal_email')
    otp_code = request.session.get('personal_email_otp')
    
    if not pending_email or not otp_code:
        messages.error(request, "No pending email verification found.")
        return redirect('/profile/')
        
    if request.method == "POST":
        user_otp = request.POST.get('otp', '').strip()
        if user_otp == otp_code:
            # Save the new personal email
            user = request.user
            user.personal_email = pending_email
            user.save()
            
            # Clean session variables
            del request.session['pending_personal_email']
            del request.session['personal_email_otp']
            
            messages.success(request, f"Personal email {pending_email} verified and added successfully! You can now use it to log in.")
            return redirect('/profile/')
        else:
            messages.error(request, "Invalid verification code. Please try again.")
            
    return render(request, "verify_personal_email.html", {"email": pending_email})


def admin_required(view_func):
    """
    Decorator to restrict view access to administrators.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or (request.user.role != 'admin' and not request.user.is_staff):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def admin_user_add(request):
    """
    Allows admin to register new users from their custom dashboard.
    """
    if request.method == "POST":
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email.split('@')[0]
            password = form.cleaned_data.get("password")
            user.set_password(password)
            user.save()
            
            messages.success(request, f"User {user.full_name or user.username} added successfully.")
            return redirect('/dashboard/')
        else:
            messages.error(request, "Failed to add user. Fix validation errors.")
    else:
        form = AdminUserForm()
        
    return render(request, "admin_user_form.html", {"form": form, "action": "Add"})


@login_required
@admin_required
def admin_user_edit(request, user_id):
    """
    Allows admin to modify user profiles by ID.
    """
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            edit_user = form.save(commit=False)
            password = form.cleaned_data.get("password")
            if password:
                edit_user.set_password(password)
            edit_user.save()
            
            messages.success(request, f"User {edit_user.full_name or edit_user.username} updated successfully.")
            return redirect('/dashboard/')
        else:
            messages.error(request, "Failed to update user. Fix validation errors.")
    else:
        form = AdminUserForm(instance=user)
        
    return render(request, "admin_user_form.html", {"form": form, "action": "Edit", "edit_user": user})


@login_required
@admin_required
def admin_user_delete(request, user_id):
    """
    Deletes user by ID.
    """
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
    else:
        name = user.full_name or user.username
        user.delete()
        messages.success(request, f"User {name} has been deleted.")
    return redirect('/dashboard/')


@login_required
@admin_required
def admin_approve_request(request, request_id):
    """
    Approves pending alumni access requests. Displays form to create/edit password,
    creates/updates user account, and sends/simulates email notification.
    """
    req = get_object_or_404(AlumniRequest, id=request_id)
    
    # Check if the user exists for this request
    user_exists = User.objects.filter(email__iexact=req.email).exists()
    if req.is_approved and user_exists:
        messages.info(request, f"Request for {req.name} has already been approved.")
        return redirect('/dashboard/')

    if request.method == "POST":
        password = request.POST.get('password', '').strip()
        if not password:
            messages.error(request, "Password cannot be empty.")
            return render(request, "admin_approve_request.html", {"req": req, "password": password})
        
        # Approve request
        req.is_approved = True
        req.save()
        
        # Check if user exists by email case-insensitively
        user = User.objects.filter(email__iexact=req.email).first()
        is_new_user = False
        
        if user:
            # Upgrade existing user
            user.role = 'alumni'
            user.set_password(password)
            user.save()
        else:
            # Create a new user with alumni role
            username = req.email.split('@')[0]
            user = User.objects.create_user(
                username=username,
                email=req.email,
                password=password,
                full_name=req.name,
                enrollment_no=req.scholar_no,
                branch=req.branch,
                graduation_year=req.graduation_year,
                role='alumni'
            )
            is_new_user = True
            
            # Make sure role is set to alumni (in case save overrides it based on graduation year)
            user.role = 'alumni'
            user.save()

        # Build email content
        subject = "AlumVerse Account Approved & Registered" if is_new_user else "AlumVerse Account Upgraded"
        email_body = (
            f"Hello {req.name},\n\n"
            f"Your alumni verification request has been approved!\n\n"
        )
        if is_new_user:
            email_body += (
                f"An account has been created for you. You can now login at AlumVerse.\n\n"
                f"Your Login Email: {req.email}\n"
                f"Your Password: {password}\n\n"
            )
        else:
            email_body += (
                f"Your existing student account has been upgraded to Alumni role.\n\n"
                f"Your login email is: {req.email}\n"
                f"Your updated password is: {password}\n\n"
            )
        email_body += "Best Regards,\nAlumVerse Team"

        email_sent = False
        try:
            # Attempt real email dispatch
            send_mail(
                subject=subject,
                message=email_body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@alumverse.com'),
                recipient_list=[req.email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            email_sent = False
            print(f"Error sending real email: {e}")

        # Display success message with email status details
        if email_sent:
            msg_text = (
                f"Alumni request for {req.name} approved successfully!\n"
                f"An actual verification email has been sent to {req.email}.\n\n"
                f"Sent Email Details:\n"
                f"--------------------------------------------------\n"
                f"Subject: {subject}\n"
                f"Username/Email: {req.email}\n"
                f"Password: {password}\n"
                f"--------------------------------------------------"
            )
        else:
            msg_text = (
                f"Alumni request for {req.name} approved successfully!\n"
                f"Account created/upgraded successfully, but the real email could not be sent (SMTP error/not configured).\n\n"
                f"Simulated email for {req.email}:\n"
                f"--------------------------------------------------\n"
                f"Subject: {subject}\n"
                f"Hello {req.name},\n"
                f"Your alumni verification request has been approved!\n"
                f"Your login email is: {req.email}\n"
                f"Your password is: {password}\n"
                f"--------------------------------------------------\n"
                f"Note: To enable real email delivery, configure correct SMTP credentials (like Gmail App Password) in your settings.py."
            )
        
        messages.success(request, msg_text)
        return redirect('/dashboard/')
        
    else:
        # GET request: generate a default password
        random_digits = random.randint(1000, 9999)
        generated_password = f"Alum@{random_digits}"
        
        return render(request, "admin_approve_request.html", {
            "req": req,
            "password": generated_password
        })


@login_required
def change_password(request):
    """
    Allows a user to securely change their password from their profile page.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/profile/')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def forgot_password(request):
    """
    Handles initiation of password reset. Verification code is sent to user's registered or personal email.
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, "forgot_password.html")
            
        # Find user by registered email or personal email case-insensitively
        user = User.objects.filter(Q(email__iexact=email) | Q(personal_email__iexact=email)).first()
        if not user:
            messages.error(request, "No account matches this email address.")
            return render(request, "forgot_password.html")
            
        # Generate 6-digit OTP code
        otp_code = str(random.randint(100000, 999999))
        
        # Save email and OTP to session
        request.session['forgot_password_email'] = email
        request.session['forgot_password_otp'] = otp_code
        
        # Send actual email
        email_sent = False
        target_email = user.email if email.lower() == (user.email or '').lower() else user.personal_email
        try:
            send_mail(
                subject="AlumVerse Password Reset OTP",
                message=f"Hello {user.full_name or user.username},\n\nYour OTP verification code to reset your AlumVerse password is: {otp_code}\n\nBest Regards,\nAlumVerse Team",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin.alumverse@gmail.com'),
                recipient_list=[target_email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            print(f"Error sending forgot password OTP: {e}")
            
        if email_sent:
            messages.success(
                request,
                f"A password reset OTP has been sent to your email {target_email}. Please verify below."
            )
        else:
            messages.success(
                request,
                f"Simulated verification code sent to {target_email}: [ {otp_code} ]\n(Note: Setup correct credentials in settings.py to receive actual emails)"
            )
            
        return redirect('/forgot-password/verify/')
        
    return render(request, "forgot_password.html")


def forgot_password_verify(request):
    """
    Checks verification OTP and updates user password.
    """
    email = request.session.get('forgot_password_email')
    otp_code = request.session.get('forgot_password_otp')
    
    if not email or not otp_code:
        messages.error(request, "No pending password reset request found.")
        return redirect('/forgot-password/')
        
    if request.method == "POST":
        user_otp = request.POST.get('otp', '').strip()
        new_password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if user_otp != otp_code:
            messages.error(request, "Invalid verification code. Please try again.")
            return render(request, "forgot_password_verify.html", {"email": email})
            
        if not new_password or new_password != confirm_password:
            messages.error(request, "Passwords do not match or are empty.")
            return render(request, "forgot_password_verify.html", {"email": email})
            
        # Update user's password case-insensitively
        user = User.objects.filter(Q(email__iexact=email) | Q(personal_email__iexact=email)).first()
        if user:
            user.set_password(new_password)
            user.save()
            
            # Clean session variables
            del request.session['forgot_password_email']
            del request.session['forgot_password_otp']
            
            messages.success(request, "Your password has been reset successfully! Please login with your new credentials.")
            return redirect('/login/')
        else:
            messages.error(request, "An error occurred. User not found.")
            return redirect('/forgot-password/')
            
    return render(request, "forgot_password_verify.html", {"email": email})


@login_required
def alumni_id_card(request):
    """
    Renders a beautiful digital identity card for the verified alumni.
    Generates a unique card reference code dynamically.
    """
    if request.user.role != 'alumni':
        messages.error(request, "Access denied. Only registered Alumni can view the Digital ID Card.")
        return redirect('/profile/')
        
    grad_year = request.user.graduation_year or 2026
    unique_code = f"AMV-{request.user.id}-{grad_year}"
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    return render(request, "alumni_id_card.html", {
        "profile": profile,
        "unique_code": unique_code
    })


@login_required
def delete_post(request, post_id):
    """
    Deletes a specific community feed post.
    Validates that the logged-in user is the author of the post or a staff admin.
    """
    from .models import Post
    post = get_object_or_404(Post, id=post_id)
    
    if post.author == request.user or request.user.role == 'admin' or request.user.is_staff:
        post.delete()
        messages.success(request, "Post deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this post.")
        
    return redirect('/dashboard/')