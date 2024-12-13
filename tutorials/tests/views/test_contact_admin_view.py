from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactAdminViewTestCase(TestCase):
    def setUp(self):
        """Set up test users with different roles."""
        self.student_user = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="Password123",
            role="student",
        )
        self.tutor_user = User.objects.create_user(
            username="tutor1",
            email="tutor1@example.com",
            password="Password123",
            role="tutor",
        )
        self.admin_user = User.objects.create_superuser(
            username="admin1",
            email="admin1@example.com",
            password="Password123",
            role="admin",
        )
        self.url = reverse("contact_admin")

    def test_student_user_contact_admin(self):
        """Test contact admin view for a student user."""
        self.client.login(username="student1", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_admin.html")
        self.assertEqual(response.context["base_template"], "dashboard_base_student.html")

    def test_tutor_user_contact_admin(self):
        """Test contact admin view for a tutor user."""
        self.client.login(username="tutor1", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_admin.html")
        self.assertEqual(response.context["base_template"], "dashboard_base_tutor.html")

    def test_admin_user_contact_admin(self):
        """Test contact admin view for an admin user."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_admin.html")
        self.assertEqual(response.context["base_template"], "dashboard_base_admin.html")

    def test_unauthenticated_user_redirect(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(reverse("log_in")))
