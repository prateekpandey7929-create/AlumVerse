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

    def test_repost_post(self):
        """
        Tests reposting another user's post.
        """
        from accounts.models import Post
        original = Post.objects.create(author=self.student, content="Original Post", category="general")
        self.assertEqual(Post.objects.count(), 1)

        response = self.client.post(f"/dashboard/repost/{original.id}/", {
            "repost_comment": "Check this original!",
            "category": "general"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 2)
        repost = Post.objects.exclude(id=original.id).first()
        self.assertEqual(repost.parent_post, original)
        self.assertEqual(repost.content, "Check this original!")

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




