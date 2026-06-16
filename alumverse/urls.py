# pyrefly: ignore [missing-import]
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

from accounts.views import (
register,
verify_otp,
user_login,
dashboard,
profile,
edit_profile,
user_logout,
notifications,
alumni_request,
add_personal_email,
verify_personal_email,
admin_user_add,
admin_user_edit,
admin_user_delete,
admin_approve_request,
admin_reject_request,
change_password,
forgot_password,
forgot_password_verify,
alumni_id_card,
delete_post,
toggle_like,
toggle_save,
increment_video_view,
add_comment,
edit_post,
repost
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
inbox,
community_chat
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

    path('verify-otp/', verify_otp),

    path('login/', user_login),

    path('logout/', user_logout),

    path('forgot-password/', forgot_password),

    path('forgot-password/verify/', forgot_password_verify),


    # ================= DASHBOARD =================

    path('dashboard/', dashboard),

    path('dashboard/delete-post/<int:post_id>/', delete_post),

    path('dashboard/like/<int:post_id>/', toggle_like),

    path('dashboard/save/<int:post_id>/', toggle_save),

    path('dashboard/video-view/<int:video_id>/', increment_video_view),

    path('dashboard/comment/<int:post_id>/', add_comment),

    path('dashboard/edit-post/<int:post_id>/', edit_post),

    path('dashboard/repost/<int:post_id>/', repost),

    path('profile/', profile),

    path('profile/change-password/', change_password),

    path('profile/add-personal-email/', add_personal_email),

    path('profile/verify-personal-email/', verify_personal_email),

    path('profile/id-card/', alumni_id_card, name='alumni_id_card'),

    path('edit-profile/', edit_profile),

    path('admin-dashboard/add-user/', admin_user_add),

    path('admin-dashboard/edit-user/<int:user_id>/', admin_user_edit),

    path('admin-dashboard/delete-user/<int:user_id>/', admin_user_delete),

    path('admin-dashboard/approve-request/<int:request_id>/', admin_approve_request),
    path('admin-dashboard/reject-request/<int:request_id>/', admin_reject_request),


    # ================= ALUMNI =================

    path('alumni/', alumni_directory),

    path('alumni-profile/<int:id>/', alumni_profile),

    path('alumni-search/', alumni_search),

    path('alumni-request/', alumni_request),


    # ================= JOBS =================

    path('jobs/', job_list),

    path('post-job/', post_opportunity),


    # ================= MESSAGING =================

    path('messages/community/', community_chat),

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
