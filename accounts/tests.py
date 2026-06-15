from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import AlumniRequest

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
