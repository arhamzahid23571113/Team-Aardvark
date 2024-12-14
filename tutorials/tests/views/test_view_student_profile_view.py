from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ViewStudentProfileTestCase(TestCase):
    def setUp(self):
        """Set up test data for the test cases."""

        self.admin = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="Password123",
            role="admin"
        )

        self.student = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="Password123",
            role="student"
        )

        self.tutor = User.objects.create_user(
            username="tutor1",
            email="tutor1@example.com",
            password="Password123",
            role="tutor"
        )

        self.url = reverse('view_student_profile', args=[self.student.id])

    def test_admin_access(self):
        """Test that an authenticated admin can access the student profile."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_student_profile.html")
        self.assertEqual(response.context["student"], self.student)

    def test_unauthenticated_user_redirect(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")


    def test_invalid_student_id_raises_404(self):
        """Test that accessing a non-existent student ID raises a 404 error."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.get(reverse('view_student_profile', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_correct_template_and_data_rendered(self):
        """Test that the correct template and student profile data is rendered."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.get(self.url)

        self.assertContains(response, self.student.username)
        self.assertContains(response, self.student.email)
