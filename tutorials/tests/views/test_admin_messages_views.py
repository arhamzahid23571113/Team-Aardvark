from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import ContactMessage

User = get_user_model()

class AdminMessagesViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""

        self.admin = User.objects.create_user(
            username="admin101",
            email="admin101@example.com",
            password="Password123",
            role="admin"
        )

        # Create student and tutor users
        self.student_user = User.objects.create_user(
            username="student101",
            email="student101@example.com",
            password="Password123",
            role="student"
        )
        self.tutor_user = User.objects.create_user(
            username="tutor101",
            email="tutor101@example.com",
            password="Password123",
            role="tutor"
        )

        self.student_message = ContactMessage.objects.create(
            user=self.student_user,
            role="student",
            message="Hello, I need help with my account.How do i book a lesson?"
        )

        self.tutor_message = ContactMessage.objects.create(
            user=self.tutor_user,
            role="tutor",
            message="Can I get support with my timetable?"
        )

        self.all_messages_url = reverse("admin_messages", kwargs={"role": "all"})
        self.student_messages_url = reverse("admin_messages", kwargs={"role": "student"})
        self.tutor_messages_url = reverse("admin_messages", kwargs={"role": "tutor"})
        self.invalid_role_url = reverse("admin_messages", kwargs={"role": "invalid"})

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.all_messages_url)
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(response.url.startswith(reverse("log_in")))


    def test_admin_access_all_messages(self):
        """Test that an admin can view all messages."""
        self.client.login(username="admin101", password="Password123")
        response = self.client.get(self.all_messages_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_messages.html")
        messages = response.context["messages"]
        self.assertEqual(len(messages), 2)  

    def test_admin_access_student_messages(self):
        """Test that an admin can filter and view only student messages."""
        self.client.login(username="admin101", password="Password123")
        response = self.client.get(self.student_messages_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_messages.html")
        messages = response.context["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], self.student_message)

    def test_admin_access_tutor_messages(self):
        """Test that an admin can filter and view only tutor messages."""
        self.client.login(username="admin101", password="Password123")
        response = self.client.get(self.tutor_messages_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_messages.html")
        messages = response.context["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], self.tutor_message)

    def test_admin_access_invalid_role(self):
        """Test that an admin sees no messages if the role is invalid."""
        self.client.login(username="admin101", password="Password123")
        response = self.client.get(self.invalid_role_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_messages.html")
        messages = response.context["messages"]
        self.assertEqual(len(messages), 0) 
