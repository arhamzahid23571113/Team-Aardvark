from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from tutorials.models import User, Invoice, LessonRequest
from tutorials.views import generate_invoice
from datetime import date

class InvoicePageTests(TestCase):
    def setUp(self):
        # Create a test user
        self.student = User.objects.create_user(
            username="@teststudent",
            first_name="Test",
            last_name="Student",
            email="test@student.com",
            role="student"
        )
        self.client.force_login(self.student)

        # Create an invoice
        self.invoice = Invoice.objects.create(
            student=self.student,
            invoice_num="INV12345",
            due_date=date(2025, 5, 31),
            payment_status="Unpaid"
        )

    def test_invoice_page_no_invoice(self):
        self.client.logout()  # Ensure the user is logged out
        response = self.client.get(reverse('invoice_page'))

        # Assert redirect to the customized login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/log_in/', response.url)  # Match the actual login URL



    @patch('tutorials.views.date')  # Replace 'tutorials' with your app name
    def test_invoice_page_autumn_term(self, mock_date):
        # Set the mocked date.today() to return a specific date
        mock_date.today.return_value = date(2024, 9, 15)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)  # Ensure side_effect mimics date behavior

        response = self.client.get(reverse('invoice_page'))

        # Validate response status and context
        self.assertEqual(response.status_code, 200)
        self.assertIn("autumn", response.context['term_name'].lower())


    def test_invoice_page_with_term_name(self):
        # Pass a valid term_name
        response = self.client.get(reverse('invoice_page_term', args=["spring"]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Spring", response.context['term_name'])

    def test_generate_invoice_logic(self):
        # Test price calculation logic
        lesson_request = LessonRequest.objects.create(
            student=self.student,
            tutor=self.student,
            requested_date=date(2024, 10, 10),
            requested_duration=120,  # 2 hours
            status="Allocated"
        )
        lesson_requests, total = generate_invoice(self.invoice, date(2024, 9, 1), date(2024, 12, 31))
        self.assertEqual(len(lesson_requests), 1)
        self.assertEqual(total, 20.00)  # Assuming £10/hour rate
