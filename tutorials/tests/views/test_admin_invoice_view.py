from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
from tutorials.models import Invoice, LessonRequest

class AdminInvoiceViewTest(TestCase):
    def setUp(self):
        # Get the custom User model
        User = get_user_model()
        
        # Create a test user and log them in
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        
        # Create an invoice for the test user
        self.invoice = Invoice.objects.create(
            student=self.user,
            invoice_num="INV12345",
            due_date=timezone.now().date() + timezone.timedelta(days=30),
            payment_status="Unpaid"
        )
        
        # Create lesson requests for the test user
        self.lesson_request_1 = LessonRequest.objects.create(
            student=self.user,
            requested_date=timezone.now().date(),
            status='Allocated',
            requested_duration=60,
            invoice=self.invoice
        )
        self.lesson_request_2 = LessonRequest.objects.create(
            student=self.user,
            requested_date=timezone.now().date() + timezone.timedelta(days=1),
            status='Allocated',
            requested_duration=90,
            invoice=self.invoice
        )
        
        # Define the URL to test
        self.url = reverse('admin_invoice_view', kwargs={'invoice_num': self.invoice.invoice_num})
    
    @patch('yourapp.views.generate_invoice')
    def test_admin_invoice_view(self, mock_generate_invoice):
        # Mock the generate_invoice function
        mock_generate_invoice.return_value = [self.lesson_request_1, self.lesson_request_2], 25.0  # Mock lesson requests and total
        
        # Make a GET request to the view
        response = self.client.get(self.url)
        
        # Check if the view returns a 200 status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct context data is passed to the template
        self.assertIn('invoice', response.context)
        self.assertIn('lesson_requests', response.context)
        self.assertIn('total', response.context)
        self.assertEqual(response.context['invoice'], self.invoice)
        self.assertEqual(response.context['total'], 25.0)
        
        # Check that the invoice's payment status is correctly set to "Unpaid"
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.payment_status, 'Unpaid')

        # Check if the correct template is rendered
        self.assertTemplateUsed(response, 'invoice_page.html')

    def test_invoice_not_found(self):
        # Test for a non-existing invoice
        response = self.client.get(reverse('admin_invoice_view', kwargs={'invoice_num': 'NONEXISTENT'}))
        self.assertEqual(response.status_code, 404)
        
    def test_invoice_without_lessons(self):
        # Test for an invoice with no lessons (should be marked as "Paid")
        empty_invoice = Invoice.objects.create(
            student=self.user,
            invoice_num="INV12346",
            due_date=timezone.now().date() + timezone.timedelta(days=30),
            payment_status="Unpaid"
        )
        
        response = self.client.get(reverse('admin_invoice_view', kwargs={'invoice_num': empty_invoice.invoice_num}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(empty_invoice.payment_status, 'Paid')  # Check that payment status is "Paid"
    
    def test_access_restricted_for_non_logged_in_users(self):
        # Log out the user
        self.client.logout()
        
        # Try accessing the view without login
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')  # Should redirect to login
