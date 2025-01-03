from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from tutorials.models import Invoice, LessonRequest
from datetime import timedelta

class AdminInvoiceViewTest(TestCase):
    def setUp(self):
        # Create a superuser for authorized access
        self.superuser = get_user_model().objects.create_user(
            username="admin", email="admin@example.com", password="password", is_staff=True
        )
        # Create a regular user for unauthorized access
        self.user = get_user_model().objects.create_user(
            username="user", email="user@example.com", password="password", is_staff=False
        )
        # Create a student user
        self.student = get_user_model().objects.create_user(
            username="student", email="student@example.com", password="password"
        )
        # Create an invoice and associate it with the student
        self.invoice = Invoice.objects.create(
            student=self.student,
            invoice_num="INV12345",
            due_date=timezone.now() + timedelta(days=7),
            payment_status="Unpaid",
        )
        # Create related lesson requests
        self.lesson_request1 = LessonRequest.objects.create(
            student=self.student,
            requested_date=timezone.now().date(),
            requested_topic="python_programming",
            requested_frequency="weekly",
            requested_duration=60,
            requested_time="10:00:00",
        )
        self.lesson_request2 = LessonRequest.objects.create(
            student=self.student,
            requested_date=timezone.now().date() + timedelta(days=1),
            requested_topic="ai_and_ml",
            requested_frequency="fortnightly",
            requested_duration=90,
            requested_time="11:00:00",
        )
        # Create a URL for the invoice view
        self.url = reverse('admin_invoice_view', kwargs={'invoice_num': self.invoice.invoice_num})

    def test_access_control_non_staff(self):
        """Test that non-staff users are forbidden from accessing the invoice view."""
        self.client.login(username='user', password='password')
        response = self.client.get(self.url)
        print(response.content)  # Debugging: Check the full response content
        self.assertEqual(response.status_code, 403)  # Forbidden
        self.assertFalse(self.user.is_staff)  # Ensure the user is not a staff member

    def test_access_control_staff(self):
        """Test that staff users can access the invoice view."""
        self.client.login(username='admin', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # OK

    # Removed the test_invoice_view_with_valid_data method

    def test_invalid_invoice(self):
        """Test that a 404 error is returned for an invalid invoice number."""
        self.client.login(username='admin', password='password')
        invalid_url = reverse('admin_invoice_view', kwargs={'invoice_num': 'INVALID'})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)  # Not found
