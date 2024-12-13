from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest

User = get_user_model()


class StudentRequestsViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create test users
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

        # Create lesson requests
        self.lesson_request = LessonRequest.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            status="Unallocated",
            requested_topic="Math",
            requested_date="2024-01-01",
            requested_time="10:00:00",
            requested_duration=60,
        )

        self.url = reverse("student_requests")

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("log_in")))

    def test_admin_access(self):
        """Test that an admin can access the page."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_requests.html")

        # Check the students_with_requests context
        students_with_requests = response.context["students_with_requests"]
        self.assertIn(self.student_user, students_with_requests)
        self.assertEqual(len(students_with_requests[self.student_user]), 1)  # One request

        # Check the tutors context
        tutors = response.context["tutors"]
        self.assertIn(self.tutor_user, tutors)

    def test_no_lesson_requests(self):
        """Test that the view handles the case where there are no lesson requests."""
        LessonRequest.objects.all().delete()  # Remove all lesson requests
        self.client.login(username="admin1", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_requests.html")

        students_with_requests = response.context["students_with_requests"]
        self.assertEqual(len(students_with_requests), 0)  # No students with requests
