from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from datetime import date
from tutorials.models import Invoice, LessonRequest

class ManageInvoicesTest(TestCase):
    def setUp(self):
        # Use the custom User model
        User = get_user_model()

        # Create a test admin user
        self.admin_user = User.objects.create_user(
            username='admin', email='admin@test.com', password='password', is_staff=True)
        
        # Create a test regular user (non-admin)
        self.regular_user = User.objects.create_user(
            username='user', email='user@test.com', password='password', is_staff=False)

        # Create test invoices for the admin user
        self.student = self.admin_user  # Assuming the admin user is a student for simplicity
        self.invoice_1 = Invoice.objects.create(
            student=self.student,
            invoice_num="INV001",
            due_date=date(2024, 12, 30),
            payment_status="Unpaid"
        )
        self.invoice_2 = Invoice.objects.create(
            student=self.student,
            invoice_num="INV002",
            due_date=date(2024, 12, 31),
            payment_status="Unpaid"
        )

    def test_manage_invoices_redirect_if_not_logged_in(self):
        # Test that a non-authenticated user is redirected to login
        response = self.client.get(reverse('manage_invoices'))
        self.assertRedirects(response, '/log_in/?next=/manage_invoices/')

    def test_manage_invoices_for_non_admin(self):
        # Test that a non-admin user cannot access the view
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('manage_invoices'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    @patch('tutorials.views.generate_invoice')  # Mock the generate_invoice function
    def test_manage_invoices_context_data(self, mock_generate_invoice):
        # Mock the lesson requests and total from generate_invoice
        mock_generate_invoice.return_value = ([], 100)

        self.client.login(username='admin', password='password')

        # Get the response from the view
        response = self.client.get(reverse('manage_invoices'))

        # Check that the status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Ensure the correct context data is passed
        self.assertIn('invoice_data', response.context)
        invoice_data = response.context['invoice_data']

        # Check the invoice data for the first invoice
        self.assertEqual(len(invoice_data), 2)  # Two invoices should be in the context
        self.assertEqual(invoice_data[0]['invoice'], self.invoice_1)
        self.assertEqual(invoice_data[0]['total'], 100)
        self.assertEqual(invoice_data[0]['lesson_requests'], [])
        self.assertEqual(self.invoice_1.payment_status, 'Unpaid')

    @patch('tutorials.views.generate_invoice')  # Mock the generate_invoice function
    def test_manage_invoices_no_invoices(self, mock_generate_invoice):
        # No invoices for the student
        mock_generate_invoice.return_value = ([], 0)

        self.client.login(username='admin', password='password')

        # Get the response from the view
        response = self.client.get(reverse('manage_invoices'))

        # Ensure the correct context data is passed
        invoice_data = response.context['invoice_data']

        # Check if invoice data is an empty list since there are no lesson requests
        self.assertEqual(len(invoice_data), 2)  # Check if two invoices are still present
        self.assertEqual(invoice_data[0]['total'], 0)
        self.assertEqual(invoice_data[1]['total'], 0)
        self.assertEqual(self.invoice_1.payment_status, 'Paid')

    def test_manage_invoices_only_admin_can_access(self):
        # Check if admin can access the view
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('manage_invoices'))
        self.assertEqual(response.status_code, 200)  # Admin should have access

        # Check if regular user cannot access the view
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('manage_invoices'))
        self.assertEqual(response.status_code, 403)  # Forbidden for regular users
