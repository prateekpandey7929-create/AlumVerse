from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

from accounts.views import (
register,
user_login,
dashboard,
profile,
edit_profile,
user_logout,
notifications,
alumni_request
)

from alumni.views import (
alumni_directory,
alumni_profile,
alumni_search
)

from jobs.views import (
post_opportunity,
job_list
)

from messaging.views import (
send_message,
inbox
)

from ai_features.views import (
alumni_recommendations,
skill_gap,
resume_analyzer,
career_path,
chatbot
)

# =========================

# DJANGO ADMIN CUSTOMIZATION

# =========================

admin.site.site_header = "AlumVerse Admin Panel"
admin.site.site_title = "AlumVerse"
admin.site.index_title = "Welcome to AlumVerse Administration"

# =========================

# URL PATTERNS

# =========================

urlpatterns = [

    # ================= HOME PAGES =================

    path('', views.home),

    path('about/', views.about),

    path('contact/', views.contact),

    path('privacy/', views.privacy),

    path('terms/', views.terms),


    # ================= AUTH =================

    path('register/', register),

    path('login/', user_login),

    path('logout/', user_logout),


    # ================= DASHBOARD =================

    path('dashboard/', dashboard),

    path('profile/', profile),

    path('edit-profile/', edit_profile),


    # ================= ALUMNI =================

    path('alumni/', alumni_directory),

    path('alumni-profile/<int:id>/', alumni_profile),

    path('alumni-search/', alumni_search),

    path('alumni-request/', alumni_request),


    # ================= JOBS =================

    path('jobs/', job_list),

    path('post-job/', post_opportunity),


    # ================= MESSAGING =================

    path('messages/<int:user_id>/', send_message),

    path('inbox/', inbox),

    path('notifications/', notifications),


    # ================= AI FEATURES =================

    path('ai-recommendations/', alumni_recommendations),

    path('skill-gap/', skill_gap),

    path('resume-analyzer/', resume_analyzer),

    path('career-path/', career_path, name='career_path'),

    path('chatbot/', chatbot),


    # ================= DJANGO ADMIN =================

    path('admin/', admin.site.urls),


]

# ================= MEDIA FILES =================

urlpatterns += static(
settings.MEDIA_URL,
document_root=settings.MEDIA_ROOT
)
