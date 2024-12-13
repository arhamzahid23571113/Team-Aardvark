from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from tutorials.models import LessonRequest

User = get_user_model()


class CancelRequestViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create users
        self.admin_user = User.objects.create_superuser(
            username="admin1",
            email="admin1@example.com",
            password="Password123",
            role="admin",
        )
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

        self.lesson_request = LessonRequest.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            status="Allocated",
            requested_topic="Ruby on Rails",
            requested_date="2024-01-10",
            requested_time="10:00:00",
            requested_duration=60,
        )

        self.url = reverse("cancel_request", args=[self.lesson_request.id])

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("log_in")))


    def test_cancel_request_successfully(self):
        """Test that an admin can successfully cancel a lesson request."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to student_requests
        self.assertRedirects(response, reverse("student_requests"))

        self.lesson_request.refresh_from_db()
        self.assertEqual(self.lesson_request.status, "Cancelled")
        self.assertIsNone(self.lesson_request.tutor)

    def test_invalid_lesson_request(self):
        """Test that an error occurs if the lesson request does not exist."""
        self.client.login(username="admin1", password="Password123")
        invalid_url = reverse("cancel_request", args=[999])  
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)  
