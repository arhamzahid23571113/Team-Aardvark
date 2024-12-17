from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import date, timedelta
from tutorials.models import Invoice, LessonRequest

User = get_user_model()

class InvoicePageViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a student user
        cls.student = User.objects.create_user(
            username='@student1',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.com',
            role='student',
            password='password123'
        )

        # Create an invoice for the student
        cls.invoice = Invoice.objects.create(
            student=cls.student,
            invoice_num='INV0001',
            due_date=date.today() + timedelta(days=10),
            payment_status='Unpaid'
        )

        # Create lesson requests for different terms
        cls.lesson_requests = [
            LessonRequest.objects.create(
                student=cls.student,
                tutor=User.objects.create_user(
                    username=f'@tutor{i}',
                    first_name=f'Tutor{i}',
                    last_name=f'Surname{i}',
                    email=f'tutor{i}@example.com',
                    role='tutor',
                    password='password123'
                ),
                request_date=date(2024, 9, 15),  # Autumn term
                requested_duration=60,
                status='Allocated'
            )
            for i in range(3)
        ]

    def setUp(self):
        # Log in the student for each test
        self.client.login(username='@student1', password='password123')

    def test_invoice_page_loads_current_term(self):
        """Test that the invoice page loads for the current term when no term_name is provided."""
        response = self.client.get(reverse('invoice_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice_page.html')
        self.assertContains(response, "Here are your invoices, John.")

    def test_invoice_page_specific_term(self):
        """Test that the invoice page loads for a specific term."""
        response = self.client.get(reverse('invoice_page_term', args=['autumn']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Autumn term")
        self.assertContains(response, "INV0001")

    def test_invoice_page_no_invoice(self):
        """Test the response when no invoice exists for the student."""
        self.invoice.delete()
        response = self.client.get(reverse('invoice_page'))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "No invoice found")

    def test_invoice_page_term_navigation(self):
        """Test navigation to previous and next terms."""
        response = self.client.get(reverse('invoice_page_term', args=['spring']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spring term")
        self.assertContains(response, "Previous Term")
        self.assertContains(response, "Next Term")

    def test_invoice_page_lesson_request_display(self):
        """Test that lesson requests are displayed correctly with pricing."""
        response = self.client.get(reverse('invoice_page_term', args=['autumn']))
        self.assertEqual(response.status_code, 200)
        for lesson in self.lesson_requests:
            self.assertContains(response, lesson.request_date.strftime("%d/%m/%Y"))
            self.assertContains(response, f"£{(lesson.requested_duration / 60 * 10):.2f}")

    def test_invoice_page_access_unauthenticated(self):
        """Test that unauthenticated users are redirected to login."""
        self.client.logout()
        response = self.client.get(reverse('invoice_page'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_invoice_page_no_lesson_requests(self):
        """Test when there are no lesson requests for the term."""
        LessonRequest.objects.all().delete()
        response = self.client.get(reverse('invoice_page_term', args=['autumn']))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "£")  # No prices listed
        self.assertContains(response, "Total: £0.00")

    def test_invoice_page_admin_user(self):
        """Test invoice page for an admin user."""
        admin_user = User.objects.create_superuser(
            username='@admin',
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            password='adminpassword123'
        )
        self.client.login(username='@admin', password='adminpassword123')
        response = self.client.get(reverse('invoice_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invoice")
        self.assertContains(response, "Admin")

