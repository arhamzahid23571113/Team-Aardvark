from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import ContactMessage

User = get_user_model()


class TutorMessagesTestCase(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(
            username='tutor1',
            email='tutor1@example.com',
            password='Password123',
            role='tutor'
        )
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin1@example.com',
            password='Password123',
            role='admin'
        )
        self.student = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='Password123',
            role='student'
        )

        self.message1 = ContactMessage.objects.create(
            user=self.tutor,
            role='tutor',
            message='Message 1 from Tutor',
        )
        self.message2 = ContactMessage.objects.create(
            user=self.tutor,
            role='tutor',
            message='Message 2 from Tutor',
        )

        self.url = reverse('tutor_messages')

    def test_tutor_can_view_own_messages(self):
        """Test that a tutor can view their own messages."""
        self.client.login(username='tutor1', password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_messages.html')
        self.assertQuerySetEqual(
            response.context['messages'],
            ContactMessage.objects.filter(user=self.tutor).order_by('timestamp'),
            transform=lambda x: x
        )

    def test_admin_can_view_tutor_messages(self):
        """Test that an admin can access the tutor_messages view."""
        self.client.login(username='admin1', password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_messages.html')

    def test_redirect_for_unauthenticated_users(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

