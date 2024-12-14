from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import ContactMessage

User = get_user_model()


class ViewStudentMessagesTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            username="admin123",
            email="admin123@example.com",
            password="Password123",
            role="admin",
        )
        self.student_user = User.objects.create_user(
            username="student123",
            email="student231@example.com",
            password="Password123",
            role="student",
        )
        self.tutor_user = User.objects.create_user(
            username="tutor123",
            email="tutor123@example.com",
            password="Password123",
            role="tutor",
        )

        self.student_message1 = ContactMessage.objects.create(
            user=self.student_user,
            role="student",
            message="Message from tutor 1",
        )
        self.student_message2 = ContactMessage.objects.create(
            user=self.student_user,
            role="student",
            message="Another message from tutor 1",
        )

        self.url = reverse("view_student_messages", kwargs={"role": "student"})

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("log_in")))

    def test_access_by_admin(self):
        """Test that an admin user can access the tutor messages view."""
        self.client.login(username="admin123", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_messages_students.html")

        messages = response.context["messages"]
        self.assertEqual(len(messages), 2)
        self.assertIn(self.student_message1, messages)
        self.assertIn(self.student_message2, messages)


    def test_no_messages(self):
        """Test behavior when there are no tutor messages."""
        self.student_message1.delete()
        self.student_message2.delete()

        self.client.login(username="admin123", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_messages_students.html")

        messages = response.context["messages"]
        self.assertEqual(len(messages), 0)