from django.test import TestCase
from django.urls import reverse
from tutorials.models import User
from unittest.mock import patch
from tutorials.models import Invoice
from datetime import date

from django.contrib.auth.models import User
import random
import string

def generate_random_email():
    # Function to generate a unique email address
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + '@example.com'

class AdminInvoiceViewTests(TestCase):
    def setUp(self):
        # Generate unique email addresses for each user
        self.admin_user = User.objects.create_user(
            username='admin', 
            email=generate_random_email(), 
            password='password', 
            is_staff=True,  # Admin user
            is_superuser=True  # Admin user
        )
        self.student_user = User.objects.create_user(
            username='student', 
            email=generate_random_email(), 
            password='password', 
            is_staff=False,  # Non-admin user
            is_superuser=False  # Non-admin user
        )

        # Create an invoice associated with the student
        self.invoice = Invoice.objects.create(
            student=self.student_user,
            invoice_num="12345678",
            due_date=date.today(),
            payment_status="Unpaid"
        )

    def test_admin_access(self):
        """Test that only admin users can access the invoice page."""
        # Log in as an admin
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('admin_invoice_view', args=[self.invoice.invoice_num]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice_page.html')
        self.assertIn('is_admin', response.context)
        self.assertTrue(response.context['is_admin'])

    def test_non_admin_access(self):
        """Test that non-admin users cannot access the invoice page."""
        # Log in as a regular user
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('admin_invoice_view', args=[self.invoice.invoice_num]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_invoice_not_found(self):
        """Test that an invalid invoice_num returns a 404 error."""
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('admin_invoice_view', args=['invalidnum']))
        self.assertEqual(response.status_code, 404)

    @patch('yourapp.views.generate_invoice')
    def test_generate_invoice_called(self, mock_generate_invoice):
        """Test that generate_invoice is called and the correct data is passed."""
        # Mock the return value of generate_invoice
        mock_generate_invoice.return_value = ([], 100)  # No lesson requests, total = 100

        # Log in as an admin
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('admin_invoice_view', args=[self.invoice.invoice_num]))

        # Verify that generate_invoice was called with the correct invoice
        mock_generate_invoice.assert_called_once_with(self.invoice)

        # Check that the correct data is passed to the template
        self.assertEqual(response.context['total'], 100)
        self.assertEqual(response.context['lesson_requests'], [])
    
    def test_invoice_template_variables(self):
        """Test that the correct template variables are passed to the template."""
        lesson_request = {
            'standardised_date': '15/12/2024',
            'requested_duration': 60,
            'tutor': self.student_user,
            'lesson_price': 30.0
        }

        # Mock the return value of generate_invoice
        with patch('yourapp.views.generate_invoice', return_value=([lesson_request], 30.0)):
            self.client.login(username='admin', password='password')
            response = self.client.get(reverse('admin_invoice_view', args=[self.invoice.invoice_num]))
            
            # Check the content of the response
            self.assertContains(response, '15/12/2024')
            self.assertContains(response, '60 min')
            self.assertContains(response, self.student_user.first_name)
            self.assertContains(response, '£30.00')
            self.assertContains(response, '£30.00')  # Total price

    def test_invoice_page_for_student(self):
        """Test that the invoice page displays the correct information for non-admin users."""
        lesson_request = {
            'standardised_date': '15/12/2024',
            'requested_duration': 60,
            'tutor': self.student_user,
            'lesson_price': 30.0
        }

        # Mock the return value of generate_invoice
        with patch('yourapp.views.generate_invoice', return_value=([lesson_request], 30.0)):
            self.client.login(username='student', password='password')
            response = self.client.get(reverse('admin_invoice_view', args=[self.invoice.invoice_num]))
            
            # Check if invoice details are shown
            self.assertContains(response, 'Here are your invoices,')
            self.assertContains(response, self.student_user.first_name)
            self.assertContains(response, '£30.00')  # Total price for student user

