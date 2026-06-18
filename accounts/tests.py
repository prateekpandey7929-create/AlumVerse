from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import AlumniRequest
from unittest.mock import patch, PropertyMock


User = get_user_model()

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_email_normalization(self):
        """
        Tests that both primary and personal emails are normalized to lowercase on save.
        """
        user = User.objects.create_user(
            username="testuser",
            email="TESTUser@IndoreInstitute.com",
            personal_email="MYPersonalEmail@Gmail.com",
            password="Password123!"
        )
        self.assertEqual(user.email, "testuser@indoreinstitute.com")
        self.assertEqual(user.personal_email, "mypersonalemail@gmail.com")

    def test_username_collision_resolution(self):
        """
        Tests that setting duplicate usernames or duplicate email prefixes yields unique usernames.
        """
        # User 1
        user1 = User.objects.create_user(
            username="conflict",
            email="conflict@example.com",
            password="Password123!"
        )
        # User 2 created with same username explicitly
        user2 = User.objects.create_user(
            username="conflict",
            email="conflict2@example.com",
            password="Password123!"
        )
        self.assertNotEqual(user1.username, user2.username)
        self.assertEqual(user2.username, "conflict1")

        # User 3 with no username but conflicting email prefix
        user3 = User(
            email="conflict@example.com"
        )
        user3.set_password("Password123!")
        user3.save()
        self.assertEqual(user3.username, "conflict2")

    def test_login_case_insensitive_and_permissive_role(self):
        """
        Tests case-insensitive login email matching and permissive student/alumni role validation.
        """
        student = User.objects.create_user(
            username="stu1",
            email="STUDENT@indoreinstitute.com",
            password="Password123!",
            role="student"
        )
        
        # Log in with lowercase email selecting "student"
        response = self.client.post("/login/", {
            "email": "student@indoreinstitute.com",
            "password": "Password123!",
            "role": "student"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")
        self.client.logout()

        # Log in with lowercase email selecting "alumni" (allowed due to permissive checks)
        response = self.client.post("/login/", {
            "email": "student@indoreinstitute.com",
            "password": "Password123!",
            "role": "alumni"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")
        self.client.logout()

    def test_login_admin(self):
        """
        Tests that admin role selection is allowed for is_staff or users with 'admin' role.
        """
        # Admin via role
        admin1 = User.objects.create_user(
            username="adm1",
            email="adminrole@indoreinstitute.com",
            password="Password123!",
            role="admin"
        )
        
        response = self.client.post("/login/", {
            "email": "ADMINROLE@indoreinstitute.com",
            "password": "Password123!",
            "role": "admin"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")
        self.client.logout()

        # Admin via is_staff
        admin2 = User.objects.create_user(
            username="adm2",
            email="adminstaff@indoreinstitute.com",
            password="Password123!",
            is_staff=True
        )
        
        response = self.client.post("/login/", {
            "email": "adminstaff@indoreinstitute.com",
            "password": "Password123!",
            "role": "admin"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")

    def test_admin_approve_request_self_healing(self):
        """
        Tests that approving an already approved AlumniRequest where user doesn't exist
        is allowed (self-healing mechanism).
        """
        req = AlumniRequest.objects.create(
            name="Ruturaj Sharma",
            email="ruturaj123@gmail.com",
            scholar_no="12345",
            branch="CSE",
            graduation_year=2024,
            is_approved=True
        )
        
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@alumverse.com",
            password="Password123!"
        )
        self.client.login(username="admin", password="Password123!")
        
        response = self.client.get(f"/admin-dashboard/approve-request/{req.id}/")
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(f"/admin-dashboard/approve-request/{req.id}/", {
            "password": "NewAlumPassword123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")
        
        user_exists = User.objects.filter(email="ruturaj123@gmail.com").exists()
        self.assertTrue(user_exists)

    def test_admin_reject_request(self):
        """
        Tests that rejecting a request deletes it and redirects back to dashboard.
        """
        req = AlumniRequest.objects.create(
            name="Reject Candidate",
            email="rejectme@gmail.com",
            scholar_no="99999",
            branch="ME",
            graduation_year=2023,
            is_approved=False
        )
        admin = User.objects.create_superuser(
            username="admin_reject_test",
            email="admin_reject_test@alumverse.com",
            password="Password123!"
        )
        self.client.login(username="admin_reject_test", password="Password123!")
        
        response = self.client.get(f"/admin-dashboard/reject-request/{req.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")
        
        # Check request is deleted
        self.assertFalse(AlumniRequest.objects.filter(id=req.id).exists())

    def test_admin_reject_nonexistent_request(self):
        """
        Tests that rejecting a request ID that doesn't exist redirects to dashboard with a warning.
        """
        admin = User.objects.create_superuser(
            username="admin_reject_nonexist",
            email="admin_reject_nonexist@alumverse.com",
            password="Password123!"
        )
        self.client.login(username="admin_reject_nonexist", password="Password123!")
        response = self.client.get("/admin-dashboard/reject-request/99999/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")

    def test_admin_approve_nonexistent_request(self):
        """
        Tests that approving a request ID that doesn't exist redirects to dashboard with a warning.
        """
        admin = User.objects.create_superuser(
            username="admin_approve_nonexist",
            email="admin_approve_nonexist@alumverse.com",
            password="Password123!"
        )
        self.client.login(username="admin_approve_nonexist", password="Password123!")
        response = self.client.get("/admin-dashboard/approve-request/99999/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")

    def test_alumni_id_card_view(self):
        """
        Tests that alumni_id_card view returns success for alumni but redirects student role.
        """
        alumni = User.objects.create_user(
            username="alumtest",
            email="alumtest@indoreinstitute.com",
            password="Password123!",
            role="alumni"
        )
        
        response = self.client.get("/profile/id-card/")
        self.assertEqual(response.status_code, 302)
        
        student = User.objects.create_user(
            username="studenttest",
            email="studenttest@indoreinstitute.com",
            password="Password123!",
            role="student"
        )
        self.client.login(username="studenttest", password="Password123!")
        response = self.client.get("/profile/id-card/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/profile/")
        self.client.logout()
        
        self.client.login(username="alumtest", password="Password123!")
        response = self.client.get("/profile/id-card/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Digital Alumni ID Card")

class CommunityFeedAndAITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username="stu_feed",
            email="stu_feed@indoreinstitute.com",
            password="Password123!",
            role="student"
        )
        self.client.login(username="stu_feed", password="Password123!")

    def test_create_valid_post(self):
        """
        Tests posting a valid message to the community feed.
        """
        from accounts.models import Post
        response = self.client.post("/dashboard/", {
            "create_post": "1",
            "content": "Hello AlumVerse! Looking forward to networking.",
            "category": "general"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")
        
        post = Post.objects.first()
        self.assertIsNotNone(post)
        self.assertEqual(post.author, self.student)
        self.assertEqual(post.category, "general")
        self.assertIn("Hello AlumVerse!", post.content)

    def test_create_moderated_post(self):
        """
        Tests that posts containing profane words are blocked.
        """
        from accounts.models import Post
        response = self.client.post("/dashboard/", {
            "create_post": "1",
            "content": "This post is a complete scam and spam.",
            "category": "general"
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify no post was created in the database
        self.assertEqual(Post.objects.count(), 0)

    def test_auto_tagging_internship(self):
        """
        Tests that writing 'internship' auto-appends '#Internship'.
        """
        from accounts.models import Post
        response = self.client.post("/dashboard/", {
            "create_post": "1",
            "content": "We have an open internship at our company.",
            "category": "internship"
        })
        self.assertEqual(response.status_code, 302)
        
        post = Post.objects.first()
        self.assertIsNotNone(post)
        self.assertIn("#Internship", post.content)

    def test_auto_tagging_job(self):
        """
        Tests that writing 'job opening' auto-appends '#JobAlert' and '#Placement'.
        """
        from accounts.models import Post
        response = self.client.post("/dashboard/", {
            "create_post": "1",
            "content": "There is a new job opening for developers.",
            "category": "job_alert"
        })
        self.assertEqual(response.status_code, 302)
        
        post = Post.objects.first()
        self.assertIsNotNone(post)
        self.assertIn("#JobAlert", post.content)
        self.assertIn("#Placement", post.content)

    def test_post_with_multiple_images(self):
        """
        Tests posting a message along with multiple images.
        """
        from django.core.files.uploadedfile import SimpleUploadedFile
        from accounts.models import Post, PostImage
        
        img1 = SimpleUploadedFile("image1.jpg", b"file_content_1", content_type="image/jpeg")
        img2 = SimpleUploadedFile("image2.png", b"file_content_2", content_type="image/png")
        
        response = self.client.post("/dashboard/", {
            "create_post": "1",
            "content": "Look at my new office space!",
            "category": "general",
            "images": [img1, img2]
        })
        self.assertEqual(response.status_code, 302)
        
        post = Post.objects.first()
        self.assertIsNotNone(post)
        self.assertEqual(post.images.count(), 2)

    def test_delete_post_success(self):
        """
        Tests that a user can delete their own post.
        """
        from accounts.models import Post
        post = Post.objects.create(author=self.student, content="Delete me please", category="general")
        self.assertEqual(Post.objects.count(), 1)
        
        response = self.client.get(f"/dashboard/delete-post/{post.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_post_unauthorized(self):
        """
        Tests that a user cannot delete another user's post.
        """
        from accounts.models import Post
        other_user = User.objects.create_user(
            username="other_u",
            email="other_u@indoreinstitute.com",
            password="Password123!"
        )
        post = Post.objects.create(author=other_user, content="Don't touch this", category="general")
        self.assertEqual(Post.objects.count(), 1)
        
        response = self.client.get(f"/dashboard/delete-post/{post.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)

    def test_post_with_video_success(self):
        """
        Tests posting a message along with a valid video.
        """
        from django.core.files.uploadedfile import SimpleUploadedFile
        from accounts.models import Post
        
        video_file = SimpleUploadedFile("sample.mp4", b"fake_video_bytes", content_type="video/mp4")
        response = self.client.post("/dashboard/", {
            "create_post": "1",
            "content": "Check out this coding tutorial!",
            "category": "general",
            "media": [video_file]
        })
        self.assertEqual(response.status_code, 302)
        
        post = Post.objects.first()
        self.assertIsNotNone(post)
        self.assertEqual(post.videos.count(), 1)

    @patch('django.core.files.uploadedfile.UploadedFile.size', new_callable=PropertyMock)
    def test_post_with_video_size_error(self, mock_size):
        """
        Tests that a post with a video exceeding 100MB is rejected.
        """
        mock_size.return_value = 101 * 1024 * 1024  # 101MB
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        from accounts.models import Post
        
        large_video = SimpleUploadedFile("large.mp4", b"small_bytes", content_type="video/mp4")
        response = self.client.post("/dashboard/", {
            "create_post": "1",
            "content": "Uploading a huge movie",
            "category": "general",
            "media": [large_video]
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify post creation rolled back / was deleted
        self.assertEqual(Post.objects.count(), 0)

    def test_post_like_toggle(self):
        """
        Tests toggling post like state via AJAX.
        """
        from accounts.models import Post
        post = Post.objects.create(author=self.student, content="Test Post", category="general")
        self.assertEqual(post.likes.count(), 0)

        # Like
        response = self.client.post(f"/dashboard/like/{post.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])
        self.assertEqual(response.json()['count'], 1)

        # Unlike
        response = self.client.post(f"/dashboard/like/{post.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['liked'])
        self.assertEqual(response.json()['count'], 0)

    def test_post_save_toggle(self):
        """
        Tests toggling post save state via AJAX.
        """
        from accounts.models import Post
        post = Post.objects.create(author=self.student, content="Test Post", category="general")

        # Save
        response = self.client.post(f"/dashboard/save/{post.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['saved'])

        # Unsave
        response = self.client.post(f"/dashboard/save/{post.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['saved'])

    def test_add_comment(self):
        """
        Tests posting a comment on a post.
        """
        from accounts.models import Post, Comment
        post = Post.objects.create(author=self.student, content="Test Post", category="general")
        self.assertEqual(post.comments.count(), 0)

        response = self.client.post(f"/dashboard/comment/{post.id}/", {
            "comment_text": "Nice post!"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(post.comments.count(), 1)
        self.assertEqual(post.comments.first().content, "Nice post!")

    def test_edit_post(self):
        """
        Tests editing own post content.
        """
        from accounts.models import Post
        post = Post.objects.create(author=self.student, content="Old Text", category="general")

        response = self.client.post(f"/dashboard/edit-post/{post.id}/", {
            "content": "Updated Text"
        })
        self.assertEqual(response.status_code, 302)
        post.refresh_from_db()
        self.assertEqual(post.content, "Updated Text")

    def test_comment_like_toggle(self):
        """
        Tests toggling comment like state via AJAX.
        """
        from accounts.models import Post, Comment
        post = Post.objects.create(author=self.student, content="Test Post", category="general")
        comment = Comment.objects.create(post=post, author=self.student, content="Test Comment")
        self.assertEqual(comment.likes.count(), 0)

        # Like comment
        response = self.client.post(f"/dashboard/comment/like/{comment.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])
        self.assertEqual(response.json()['count'], 1)

        # Unlike comment
        response = self.client.post(f"/dashboard/comment/like/{comment.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['liked'])
        self.assertEqual(response.json()['count'], 0)

    def test_reply_to_comment(self):
        """
        Tests creating a nested reply to a comment.
        """
        from accounts.models import Post, Comment
        post = Post.objects.create(author=self.student, content="Test Post", category="general")
        parent_comment = Comment.objects.create(post=post, author=self.student, content="Parent Comment")

        response = self.client.post(f"/dashboard/comment/reply/{parent_comment.id}/", {
            "reply_text": "This is a nested reply"
        })
        self.assertEqual(response.status_code, 302)
        
        reply = Comment.objects.filter(parent=parent_comment).first()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.content, "This is a nested reply")
        self.assertEqual(reply.post, post)

    def test_repost_disabled(self):
        """
        Tests that the repost endpoint is removed / disabled.
        """
        from accounts.models import Post
        post = Post.objects.create(author=self.student, content="Test Post", category="general")
        response = self.client.post(f"/dashboard/repost/{post.id}/", {
            "repost_comment": "Try to repost"
        })
        self.assertEqual(response.status_code, 404)

    def test_profile_views_count(self):
        """
        Tests that viewing another user's profile increments their views_count,
        but viewing one's own profile does not.
        """
        # Create an alumni user
        alumni = User.objects.create_user(
            username="alum_view_test",
            email="alum_view_test@indoreinstitute.com",
            password="Password123!",
            role="alumni"
        )
        
        # Initial view count should be 0
        self.assertEqual(alumni.profile.views_count, 0)
        
        # Current logged in user is self.student. They view alumni profile.
        response = self.client.get(f"/alumni-profile/{alumni.id}/")
        self.assertEqual(response.status_code, 200)
        
        # alumni views_count should be 1 now
        alumni.profile.refresh_from_db()
        self.assertEqual(alumni.profile.views_count, 1)
        
        # Now alumni logs in and views their own profile page.
        self.client.logout()
        self.client.login(username="alum_view_test", password="Password123!")
        
        response = self.client.get(f"/alumni-profile/{alumni.id}/")
        self.assertEqual(response.status_code, 200)
        
        # Own view should NOT increment views_count
        alumni.profile.refresh_from_db()
        self.assertEqual(alumni.profile.views_count, 1)

    def test_profile_my_and_saved_posts(self):
        """
        Tests that user's own profile view contains correct querysets for my_posts and saved_posts.
        """
        from accounts.models import Post
        # Create a post by this student
        my_post = Post.objects.create(
            author=self.student,
            content="My student post",
            category="general"
        )
        
        # Create another post and save it
        other_user = User.objects.create_user(
            username="other_auth",
            email="other_auth@gmail.com",
            password="Password123!"
        )
        saved_post = Post.objects.create(
            author=other_user,
            content="Saved other post",
            category="general"
        )
        saved_post.saves.add(self.student)
        
        # Request profile
        response = self.client.get("/profile/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("my_posts", response.context)
        self.assertIn("saved_posts", response.context)
        
        self.assertEqual(list(response.context["my_posts"]), [my_post])
        self.assertEqual(list(response.context["saved_posts"]), [saved_post])

    def test_profile_completion_percentage(self):
        """
        Tests that completion_percentage computes correct values for both student and alumni roles.
        """
        # Test student completion (initially empty, so 0%)
        student_profile = self.student.profile
        self.assertEqual(student_profile.completion_percentage, 0)
        
        # Update some fields for student
        student_profile.bio = "High-achieving student"
        student_profile.skills = "Python, Django"
        student_profile.save()
        # 2 fields filled out of 8 = 25%
        self.assertEqual(student_profile.completion_percentage, 25)
        
        # Test alumni completion
        alumni = User.objects.create_user(
            username="alum_comp",
            email="alum_comp@indoreinstitute.com",
            password="Password123!",
            role="alumni"
        )
        alumni_profile = alumni.profile
        self.assertEqual(alumni_profile.completion_percentage, 0)
        
        alumni_profile.bio = "Experienced developer"
        alumni_profile.company = "Google"
        alumni_profile.save()
        # 2 fields filled out of 11 = 18% (rounded from 18.18%)
        self.assertEqual(alumni_profile.completion_percentage, 18)


class NotificationAndAdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create student user
        self.student = User.objects.create_user(
            username="student_user",
            email="student@indoreinstitute.com",
            password="Password123!",
            role="student"
        )
        # Create alumni user
        self.alumni = User.objects.create_user(
            username="alumni_user",
            email="alumni@indoreinstitute.com",
            password="Password123!",
            role="alumni"
        )
        # Create admin user
        self.admin = User.objects.create_user(
            username="admin_user",
            email="admin@indoreinstitute.com",
            password="Password123!",
            role="admin",
            is_staff=True,
            is_superuser=True
        )

    def test_notification_clearing_on_chat_view(self):
        """
        Tests that viewing a direct chat marks message notifications from that sender as read.
        """
        from messaging.models import Message
        from accounts.models import Notification

        self.client.login(username="student_user", password="Password123!")

        # Create a message from alumni to student
        Message.objects.create(
            sender=self.alumni,
            receiver=self.student,
            message="Hello Student!"
        )
        # Create corresponding notification
        Notification.objects.create(
            user=self.student,
            message=f"New message from {self.alumni.username}"
        )

        self.assertEqual(Notification.objects.filter(user=self.student, is_read=False).count(), 1)

        response = self.client.get(f"/messages/{self.alumni.id}/")
        self.assertEqual(response.status_code, 200)

        # Notification should be read
        self.assertEqual(Notification.objects.filter(user=self.student, is_read=False).count(), 0)

    def test_notification_clearing_on_job_view(self):
        """
        Tests that visiting the jobs hub clears opportunity notifications for students.
        """
        from jobs.models import Opportunity
        from accounts.models import Notification

        import datetime
        Opportunity.objects.create(
            title="Software Intern",
            company="Google",
            description="Good coding skills required.",
            location="Remote",
            deadline=datetime.date.today(),
            type="internship",
            posted_by=self.alumni
        )
        Notification.objects.create(
            user=self.student,
            message="New internship posted: Software Intern"
        )
        
        self.assertEqual(Notification.objects.filter(user=self.student, is_read=False).count(), 1)

        self.client.login(username="student_user", password="Password123!")
        response = self.client.get("/jobs/")
        self.assertEqual(response.status_code, 200)

        # Notification should be read
        self.assertEqual(Notification.objects.filter(user=self.student, is_read=False).count(), 0)

    def test_rules_violation_moderation_logs(self):
        """
        Tests that blocked profane posts/comments log rules violations.
        """
        from accounts.models import Notification
        self.client.login(username="student_user", password="Password123!")

        response = self.client.post("/dashboard/", {
            "create_post": "1",
            "content": "This is absolute spam and nonsense.",
            "category": "general"
        })
        self.assertEqual(response.status_code, 302)

        violation = Notification.objects.filter(user=self.student).first()
        self.assertIsNotNone(violation)
        self.assertIn("[Rules Violation]", violation.message)

    def test_admin_notifications_and_warning_dispatch(self):
        """
        Tests the admin notifications dashboard and the dispatch of warnings.
        """
        from accounts.models import Notification
        from django.core import mail

        self.client.login(username="admin_user", password="Password123!")

        response = self.client.get("/admin-dashboard/notifications/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/admin-dashboard/send-warning/{self.student.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/admin-dashboard/notifications/?tab=rules")

        warning_notif = Notification.objects.filter(user=self.student, message__icontains="warning").first()
        self.assertIsNotNone(warning_notif)
        
        self.assertTrue(len(mail.outbox) >= 1)

    def test_admin_notifications_deduplication(self):
        """
        Tests that duplicate notifications are hidden/deduplicated in the admin notifications dashboard.
        """
        from accounts.models import Notification
        
        # Create duplicate notifications
        Notification.objects.create(user=self.student, message="New job posted: DevOps Engineer")
        Notification.objects.create(user=self.alumni, message="New job posted: DevOps Engineer")
        
        self.client.login(username="admin_user", password="Password123!")
        
        response = self.client.get("/admin-dashboard/notifications/?tab=job")
        self.assertEqual(response.status_code, 200)
        
        # Verify only 1 notification is rendered in the job tab
        self.assertEqual(len(response.context["job_notifications"]), 1)

    def test_navbar_bell_hidden_for_admin(self):
        """
        Tests that the navbar notification bell icon is hidden for admin users.
        """
        # When logged in as student, bell is visible
        self.client.login(username="student_user", password="Password123!")
        response = self.client.get("/dashboard/")
        self.assertContains(response, 'title="Notifications"')

        # When logged in as admin, bell is hidden
        self.client.login(username="admin_user", password="Password123!")
        response = self.client.get("/dashboard/")
        self.assertNotContains(response, 'title="Notifications"')

    def test_clear_notifications_route(self):
        """
        Tests that calling the clear notifications route deletes all notifications for the user.
        """
        from accounts.models import Notification
        
        Notification.objects.create(user=self.student, message="Test Notification 1")
        Notification.objects.create(user=self.student, message="Test Notification 2")
        
        self.assertEqual(Notification.objects.filter(user=self.student).count(), 2)
        
        self.client.login(username="student_user", password="Password123!")
        response = self.client.get("/notifications/clear/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/notifications/")
        
        # Verify they are deleted
        self.assertEqual(Notification.objects.filter(user=self.student).count(), 0)

    def test_notifications_page_clears_messages_count(self):
        """
        Tests that visiting the notifications page marks all messages as read.
        """
        from messaging.models import Message
        
        Message.objects.create(sender=self.alumni, receiver=self.student, message="Test message")
        
        self.client.login(username="student_user", password="Password123!")
        
        # Verify message is unread
        self.assertEqual(Message.objects.filter(receiver=self.student, is_read=False).count(), 1)
        
        # Visit notifications page
        response = self.client.get("/notifications/")
        self.assertEqual(response.status_code, 200)
        
        # Verify message is marked as read
        self.assertEqual(Message.objects.filter(receiver=self.student, is_read=False).count(), 0)

    def test_job_alert_to_student_and_alumni(self):
        """
        Tests that posting an opportunity sends alert notifications to both students and alumni.
        """
        from accounts.models import Notification
        
        # Admin posts a job
        self.client.login(username="admin_user", password="Password123!")
        
        response = self.client.post("/post-job/", {
            "title": "Staff Engineer",
            "company": "Amazon",
            "description": "Amazon is hiring.",
            "location": "New York",
            "deadline": "2027-12-31",
            "type": "job"
        })
        self.assertEqual(response.status_code, 302)
        
        # Check student received alert
        student_alert = Notification.objects.filter(user=self.student, message__icontains="Staff Engineer").first()
        self.assertIsNotNone(student_alert)
        
        # Check alumni received alert
        alumni_alert = Notification.objects.filter(user=self.alumni, message__icontains="Staff Engineer").first()
        self.assertIsNotNone(alumni_alert)

    def test_personalized_like_comment_notifications(self):
        """
        Tests that notifications for post likes and comments contain the user's full name.
        """
        from accounts.models import Post, Notification
        
        # Let's assign a full name to self.alumni
        self.alumni.full_name = "Jane Doe"
        self.alumni.save()
        
        # Student creates a post
        post = Post.objects.create(author=self.student, content="Personalized test post", category="general")
        
        # Alumni likes the post
        self.client.login(username="alumni_user", password="Password123!")
        response = self.client.post(f"/dashboard/like/{post.id}/")
        self.assertEqual(response.status_code, 200)
        
        # Check notification message for student (post author)
        like_notif = Notification.objects.filter(user=self.student, message__icontains="liked your post").first()
        self.assertIsNotNone(like_notif)
        self.assertIn("Jane Doe", like_notif.message)
        
        # Alumni comments on the post
        response = self.client.post(f"/dashboard/comment/{post.id}/", {
            "comment_text": "Interesting post!"
        })
        self.assertEqual(response.status_code, 302)
        
        # Check comment notification message for student
        comment_notif = Notification.objects.filter(user=self.student, message__icontains="commented on your post").first()
        self.assertIsNotNone(comment_notif)
        self.assertIn("Jane Doe", comment_notif.message)






