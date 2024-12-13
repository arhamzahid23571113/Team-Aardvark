from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AllStudentProfilesViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Password123",
            role="admin"
        )
        self.tutor_user = User.objects.create_user(
            username="tutor",
            email="tutor@example.com",
            password="Password123",
            role="tutor"
        )
        self.student_user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="Password123",
            role="student"
        )

        # URL for the view
        self.url = reverse("all_students")

    def test_admin_access(self):
        """Test that an admin can access the view and see all students."""
        self.client.login(username="admin", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "all_student_profiles.html")
        students = response.context["students"]
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].username, "student")

    def test_no_students(self):
        """Test behavior when no students exist."""
        User.objects.filter(role="student").delete()  # Remove all students
        self.client.login(username="admin", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "all_student_profiles.html")
        students = response.context["students"]
        self.assertEqual(len(students), 0)

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")
