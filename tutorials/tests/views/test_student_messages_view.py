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
            user=self.student,
            role='student',
            message='Message 1 from Student',
        )
        self.message2 = ContactMessage.objects.create(
            user=self.student,
            role='student',
            message='Message 2 from Student',
        )

        self.url = reverse('student_messages')

    def test_student_can_view_own_messages(self):
        """Test that a tutor can view their own messages."""
        self.client.login(username='student1', password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_messages.html')
        self.assertQuerySetEqual(
            response.context['messages'],
            ContactMessage.objects.filter(user=self.student).order_by('timestamp'),
            transform=lambda x: x
        )

    def test_admin_can_view_student_messages(self):
        """Test that an admin can access the student_messages view."""
        self.client.login(username='admin1', password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_messages.html')

    def test_redirect_for_unauthenticated_users(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")