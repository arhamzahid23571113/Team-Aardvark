from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ViewTutorProfileTestCase(TestCase):
    def setUp(self):
        """Set up test data for the test cases."""
        self.admin = User.objects.create_user(
            username="admin134",
            email="admin134@example.com",
            password="Password123",
            role="admin"
        )

        self.tutor = User.objects.create_user(
            username="tutor143",
            email="tutor143@example.com",
            password="Password123",
            role="tutor"
        )
        
        self.student = User.objects.create_user(
            username="student122",
            email="student122@example.com",
            password="Password123",
            role="student"
        )

        self.url = reverse('view_tutor_profile', args=[self.tutor.id])

    def test_admin_access(self):
        """Test that an authenticated admin can access the tutor profile."""
        self.client.login(username="admin134", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_tutor_profile.html")
        self.assertEqual(response.context["tutor"], self.tutor)

    def test_unauthenticated_user_redirect(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")



    def test_invalid_tutor_id_raises_404(self):
        """Test that accessing a non-existent tutor ID raises a 404 error."""
        self.client.login(username="admin134", password="Password123")
        response = self.client.get(reverse('view_tutor_profile', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_correct_template_and_data_rendered(self):
        """Test that the correct template and tutor profile data is rendered."""
        self.client.login(username="admin134", password="Password123")
        response = self.client.get(self.url)

        self.assertContains(response, self.tutor.username)
        self.assertContains(response, self.tutor.email)
