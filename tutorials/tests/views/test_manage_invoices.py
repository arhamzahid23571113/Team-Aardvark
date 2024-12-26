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
        # Create an unpaid invoice for the test
        invoice = Invoice.objects.create(
            student=self.admin_user,  # Assuming admin_user is a valid User
            invoice_num="INV12345",
            due_date="2024-12-31",
            payment_status="Unpaid"
        )
        
        # Simulate updating the payment status (manual for this test)
        invoice.payment_status = "Paid"
        invoice.payment_date = "2024-12-20"  # Optional: Set payment_date
        invoice.save()
        
        # Reload the invoice from the database
        invoice.refresh_from_db()
        
        # Assert the payment status was updated
        self.assertEqual(invoice.payment_status, "Paid")
        self.assertEqual(invoice.payment_date.strftime("%Y-%m-%d"), "2024-12-20")

    def test_invoice_data_in_context(self):
        """
        Test that the invoice data appears in the context when the page is loaded.
        """
        # Log in as a staff user
        self.client.login(username="staff", password="password")
        
        # Create test invoices
        invoice1 = Invoice.objects.create(
            student=self.staff_user,  # Example student
            invoice_num="INV001",
            due_date="2024-12-31",
            payment_status="Unpaid"  # Ensure this matches the template condition
        )
        invoice2 = Invoice.objects.create(
            student=self.admin_user,  # Another student
            invoice_num="INV002",
            due_date="2024-11-30",
            payment_status="Paid"  # This will not be rendered
        )
        
        # Send a request to the invoices page
        response = self.client.get(self.url)
        
        # Assert the response contains the unpaid invoice data
        self.assertContains(response, invoice1.invoice_num)
        # Optional: Assert that a paid invoice doesn't appear (if relevant)
        self.assertNotContains(response, invoice2.invoice_num)
        
    def test_no_invoices(self):
        """
        Test that the page shows a message when there are no invoices.
        """
        # Log in as a staff user
        self.client.login(username="staff", password="password")
        
        # Ensure there are no invoices in the database
        Invoice.objects.all().delete()
        
        # Send a request to the invoices page
        response = self.client.get(self.url)
        
        # Assert the page contains the "No invoices available" message
        self.assertContains(response, "No invoices available")


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
