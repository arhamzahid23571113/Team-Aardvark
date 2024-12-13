from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class ResponseSubmittedSuccessTest(TestCase):

    def setUp(self):
        # Create test users with different roles
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
            role='admin'
        )

    def test_tutor_user_redirect(self):
        """Test response for tutor user."""
        self.client.login(username="tutor1", password="Password123")
        response = self.client.get(reverse("response_success"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "response_submitted.html")
        self.assertEqual(response.context["base_template"], "dashboard_base_tutor.html")
        self.assertEqual(response.context["dashboard_url"], reverse("tutor_dashboard"))

    def test_student_user_redirect(self):
        """Test response for student user."""
        self.client.login(username="student1", password="Password123")
        response = self.client.get(reverse("response_success"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "response_submitted.html")
        self.assertEqual(response.context["base_template"], "dashboard_base_student.html")
        self.assertEqual(response.context["dashboard_url"], reverse("student_dashboard"))

    def test_admin_user_redirect(self):
        """Test response for admin user."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.get(reverse("response_success"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "response_submitted.html")
        self.assertEqual(response.context["base_template"], "dashboard_base_admin.html")
        self.assertEqual(response.context["dashboard_url"], reverse("admin_dashboard"))

    def test_unauthenticated_user_redirect(self):
        """Test response for an unauthenticated user."""
        response = self.client.get(reverse("response_success"))
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertTrue(response.url.startswith(reverse("log_in")))

