from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import ContactMessage
from tutorials.forms import ContactMessages

User = get_user_model()

class SendMessageToAdminViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        self.student_user = User.objects.create_user(
            username="student123",
            email="student123@example.com",
            password="Password123",
            role="student",
        )
        self.tutor_user = User.objects.create_user(
            username="tutor123",
            email="tutor123@example.com",
            password="Password123",
            role="tutor",
        )
        self.admin_user = User.objects.create_superuser(
            username="admin123",
            email="admin123@example.com",
            password="Password123",
            role="admin",
        )

        self.url = reverse("send_message_to_admin")

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(response.url.startswith(reverse("log_in")))

    def test_get_request_student(self):
        """Test the GET request for a student user."""
        self.client.login(username="student123", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_admin.html")
        self.assertIsInstance(response.context["form"], ContactMessages)
        self.assertEqual(response.context["base_template"], "dashboard_base_student.html")

    def test_get_request_tutor(self):
        """Test the GET request for a tutor user."""
        self.client.login(username="tutor123", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_admin.html")
        self.assertIsInstance(response.context["form"], ContactMessages)
        self.assertEqual(response.context["base_template"], "dashboard_base_tutor.html")

    def test_get_request_admin(self):
        """Test the GET request for an admin user."""
        self.client.login(username="admin123", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_admin.html")
        self.assertIsInstance(response.context["form"], ContactMessages)
        self.assertEqual(response.context["base_template"], "dashboard_base_admin.html")

    def test_post_valid_form_student(self):
        """Test a valid POST request from a student."""
        self.client.login(username="student123", password="Password123")
        form_data = {
            "role": "student",
            "message": "This is a test message.",
        }
        response = self.client.post(self.url, form_data)

        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.first()
        self.assertEqual(message.user, self.student_user)
        self.assertEqual(message.role, "student")
        self.assertEqual(message.message, "This is a test message.")

        self.assertRedirects(response, reverse("response_success"))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Your message has been submitted successfully!")

    def test_post_valid_form_tutor(self):
        """Test a valid POST request from a tutor."""
        self.client.login(username="tutor123", password="Password123")
        form_data = {
            "role": "tutor",
            "message": "This is a test message from tutor.",
        }
        response = self.client.post(self.url, form_data)

        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.first()
        self.assertEqual(message.user, self.tutor_user)
        self.assertEqual(message.role, "tutor")
        self.assertEqual(message.message, "This is a test message from tutor.")

        self.assertRedirects(response, reverse("response_success"))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Your message has been submitted successfully!")

    def test_post_invalid_form(self):
        """Test an invalid POST request."""
        self.client.login(username="student123", password="Password123")
        form_data = {
            "role": "",  
            "message": "",  
        }
        response = self.client.post(self.url, form_data)

        self.assertEqual(ContactMessage.objects.count(), 0)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_admin.html")
        self.assertFalse(response.context["form"].is_valid())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "There was an error with your submission.")
