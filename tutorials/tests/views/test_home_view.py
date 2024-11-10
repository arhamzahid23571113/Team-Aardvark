"""Tests for the home view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class HomeViewTestCase(TestCase):
    """Tests for the home view."""

    fixtures = ['tutorials/tests/fixtures/default_user.json']

    def setUp(self):
        """Set up test data and URL for the home view."""
        self.url = reverse('home')
        self.user = User.objects.get(username='@johndoe')

    def test_home_url_resolves_correctly(self):
        """Test that the home URL resolves to '/'."""
        self.assertEqual(self.url, '/')

    def test_get_home_as_anonymous_user(self):
        """Test that the home page renders for unauthenticated users."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirects_when_authenticated(self):
        """Test that authenticated users are redirected to the dashboard."""
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTemplateUsed(response, 'dashboard.html')
