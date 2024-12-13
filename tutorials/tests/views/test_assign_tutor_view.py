from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest

User = get_user_model()

class AssignTutorViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create users
        self.admin_user = User.objects.create_superuser(
            username="admin1",
            email="admin1@example.com",
            password="Password123",
            role="admin",
        )
        self.tutor_user = User.objects.create_user(
            username="tutor1",
            email="tutor1@example.com",
            password="Password123",
            role="tutor",
        )
        self.student_user = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="Password123",
            role="student",
        )

        # Create a lesson request
        self.lesson_request = LessonRequest.objects.create(
            student=self.student_user,
            tutor=None,
            status="Unallocated",
            requested_topic="Math",
            requested_date="2024-01-01",
            requested_time="10:00:00",
            requested_duration=60,
        )

        self.url = reverse("assign_tutor", args=[self.lesson_request.id])

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.post(self.url, {"tutor_id": self.tutor_user.id})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("log_in")))

   

    def test_assign_tutor_successfully(self):
        """Test that an admin can successfully assign a tutor."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.post(self.url, {"tutor_id": self.tutor_user.id})
        self.assertEqual(response.status_code, 302)  # Redirect to student_requests
        self.assertRedirects(response, reverse("student_requests"))

        # Verify the lesson request was updated
        self.lesson_request.refresh_from_db()
        self.assertEqual(self.lesson_request.tutor, self.tutor_user)
        self.assertEqual(self.lesson_request.status, "Allocated")

    def test_assign_tutor_invalid_tutor(self):
        """Test that an error occurs if an invalid tutor is assigned."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.post(self.url, {"tutor_id": 999})  
        self.assertEqual(response.status_code, 404)  # Should raise a 404 error

    def test_assign_tutor_missing_tutor_id(self):
        """Test that no changes occur if tutor_id is not provided."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.post(self.url, {})  
        self.assertEqual(response.status_code, 302)  # Redirect to student_requests
        self.assertRedirects(response, reverse("student_requests"))

        # Verify the lesson request remains unchanged
        self.lesson_request.refresh_from_db()
        self.assertIsNone(self.lesson_request.tutor)
        self.assertEqual(self.lesson_request.status, "Unallocated")

    def test_invalid_lesson_request(self):
        """Test that an error occurs if the lesson request does not exist."""
        self.client.login(username="admin1", password="Password123")
        url = reverse("assign_tutor", args=[999])  
        response = self.client.post(url, {"tutor_id": self.tutor_user.id})
        self.assertEqual(response.status_code, 404)  
