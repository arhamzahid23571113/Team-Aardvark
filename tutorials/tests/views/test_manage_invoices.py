from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from tutorials.models import Invoice  # Import the Invoice model (replace 'yourapp' with the actual app name)

class ManageInvoicesViewTest(TestCase):
    
    def setUp(self):
        """
        Setup for the tests, ensuring unique emails for user creation.
        """
        # Create a superuser (admin user) for the test
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )
        
        # Create a non-staff user for testing permissions
        self.non_staff_user = get_user_model().objects.create_user(
            username="nonstaff",
            email="nonstaff@example.com",  # Ensure unique email
            password="password",
            is_staff=False
        )
        
        # Create a staff user for testing
        self.staff_user = get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",  # Ensure unique email
            password="password",
            is_staff=True
        )
        
        # URL to test the invoices page
        self.url = reverse('manage_invoices')  # Adjust this to the actual URL name

    def test_generate_invoice_updates_payment_status(self):
        """
        Test that generating an invoice updates the payment status.
        """
        # Create an invoice with pending status
        invoice = Invoice.objects.create(user=self.admin_user, amount=100, status='pending')
        
        # Generate the invoice (assuming there's a method to handle this)
        invoice.generate_invoice()  # Ensure the method exists and updates status
        
        # Reload the invoice from the database
        invoice.refresh_from_db()
        
        # Check if the status is updated correctly
        self.assertEqual(invoice.status, 'paid')
    
    def test_invoice_data_in_context(self):
        """
        Test that the invoice data appears in the context when the page is loaded.
        """
        # Log in as a staff user
        self.client.login(username='staff', password='password')
        
        # Send a request to the invoices management page
        response = self.client.get(self.url)
        
        # Check if the response contains invoice data (adjust based on actual content)
        self.assertContains(response, '<tr>')  # Example check, adjust based on your HTML structure
        
    def test_no_invoices(self):
        """
        Test that the page shows a message when there are no invoices.
        """
        # Log in as a staff user
        self.client.login(username='staff', password='password')
        
        # Send a request to the invoices management page with no invoices
        response = self.client.get(self.url)
        
        # Check for a message indicating no invoices (adjust based on actual template logic)
        self.assertContains(response, 'No invoices available')

    def test_non_staff_user_forbidden(self):
        """
        Test that a non-staff user is forbidden from accessing the invoices page.
        """
        # Log in as a non-staff user
        self.client.login(username='nonstaff', password='password')
        
        # Send a request to the invoices management page
        response = self.client.get(self.url)
        
        # Check for a forbidden response
        self.assertEqual(response.status_code, 403)  # Forbidden access

    def test_staff_user_access(self):
        """
        Test that a staff user is allowed to access the invoices page.
        """
        # Log in as a staff user
        self.client.login(username='staff', password='password')
        
        # Send a request to the invoices management page
        response = self.client.get(self.url)
        
        # Check that the response status is OK
        self.assertEqual(response.status_code, 200)
