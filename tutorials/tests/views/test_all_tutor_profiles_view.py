from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AllTutorProfilesViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create users with different roles
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
        self.tutor1 = User.objects.create_user(
            username="tutor1",
            email="tutor1@example.com",
            password="Password123",
            role="tutor",
        )
        self.tutor2 = User.objects.create_user(
            username="tutor2",
            email="tutor2@example.com",
            password="Password123",
            role="tutor",
        )

        self.url = reverse("all_tutor_profiles")  # URL for the view

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("log_in")))

    def test_admin_access(self):
        """Test that an admin can access the view and see all tutors."""
        self.client.login(username="admin1", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "all_tutor_profiles.html")

        # Verify that all tutors are included in the context
        tutors = response.context["tutors"]
        self.assertEqual(tutors.count(), 2)  # There are two tutors
        self.assertIn(self.tutor1, tutors)
        self.assertIn(self.tutor2, tutors)

    def test_no_tutors(self):
        """Test behavior when no tutors exist."""
        self.tutor1.delete()
        self.tutor2.delete()

        self.client.login(username="admin1", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "all_tutor_profiles.html")

        # Verify that no tutors are displayed
        tutors = response.context["tutors"]
        self.assertEqual(tutors.count(), 0)
