from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import ContactMessage
from django.utils.timezone import now

User = get_user_model()


class AdminReplyTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin123",
            email="admin123@example.com",
            password="Password123",
            role="admin",
        )

        self.student_user = User.objects.create_user(
            username="student123",
            email="student123@example.com",
            password="Password123",
            role="student",
        )

        self.message = ContactMessage.objects.create(
            user=self.student_user,
            role="student",
            message="Hello Admin, I need help.",
        )

        self.url = reverse("admin_reply", kwargs={"message_id": self.message.id})

    def test_redirect_if_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("log_in")))

    def test_redirect_if_not_admin(self):
        self.client.login(username="student123", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("log_in")))

    def test_admin_access_get_request(self):
        self.client.login(username="admin123", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_reply.html")
        self.assertEqual(response.context["message"], self.message)

    def test_admin_submit_valid_reply(self):
        self.client.login(username="admin123", password="Password123")
        response = self.client.post(self.url, {
            "reply": "Thank you for your message. We will assist you shortly."
        })
        self.assertRedirects(response, reverse("response_success"))
        self.message.refresh_from_db()
        self.assertEqual(self.message.reply, "Thank you for your message. We will assist you shortly.")
        self.assertIsNotNone(self.message.reply_timestamp)

    def test_admin_submit_invalid_reply(self):
        self.client.login(username="admin123", password="Password123")
        response = self.client.post(self.url, {"reply": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_reply.html")
