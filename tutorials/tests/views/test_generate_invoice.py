from django.test import TestCase
from datetime import date, datetime
from django.utils import timezone
from tutorials.models import Invoice, LessonRequest, User  # Use custom User model
from django.conf import settings
from tutorials.views import generate_invoice


class GenerateInvoiceTestCase(TestCase):
    def setUp(self):
        """Set up test data for invoice and lesson requests."""
        # Create a test user
        self.student = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='password'
        )

        # Convert date to datetime and then make it aware
        due_date = datetime.combine(date(2024, 12, 31), datetime.min.time())  # Convert to datetime
        due_date = timezone.make_aware(due_date)  # Make aware

        # Create a test invoice for the student
        self.invoice = Invoice.objects.create(
            student=self.student,
            invoice_num='INV12345',
            due_date=due_date,
            payment_status='Unpaid'
        )

        # Set the hourly rate for pricing
        settings.HOURLY_RATE = 20  # $20 per hour

    def test_generate_invoice_no_term_dates(self):
        """Test generate_invoice without term start and end dates."""
        # Create lesson requests with timezone-aware dates
        lesson_request_1 = LessonRequest.objects.create(
            student=self.student,
            request_date=timezone.make_aware(datetime.combine(date(2024, 10, 15), datetime.min.time())),
            requested_duration=90,  # 90 minutes
            status='Allocated'
        )

        lesson_request_2 = LessonRequest.objects.create(
            student=self.student,
            request_date=timezone.make_aware(datetime.combine(date(2024, 11, 5), datetime.min.time())),
            requested_duration=60,  # 60 minutes
            status='Allocated'
        )

        lesson_requests, total = generate_invoice(self.invoice)

        # Ensure there are 2 lesson requests
        self.assertEqual(len(lesson_requests), 2)

        # Check the total price is correct (90 mins + 60 mins = 150 mins = 2.5 hours)
        self.assertEqual(total, 2.5 * settings.HOURLY_RATE)

        # Check if the payment status is still 'Unpaid'
        self.assertEqual(self.invoice.payment_status, 'Unpaid')

    def test_generate_invoice_with_term_dates(self):
        """Test generate_invoice with term start and end dates."""
        term_start = timezone.make_aware(datetime.combine(date(2024, 9, 1), datetime.min.time()))
        term_end = timezone.make_aware(datetime.combine(date(2024, 10, 31), datetime.min.time()))

        # Create lesson requests that match and do not match the term range
        lesson_request_1 = LessonRequest.objects.create(
            student=self.student,
            request_date=timezone.make_aware(datetime.combine(date(2024, 10, 15), datetime.min.time())),
            requested_duration=90,  # 90 minutes
            status='Allocated'
        )

        lesson_request_2 = LessonRequest.objects.create(
            student=self.student,
            request_date=timezone.make_aware(datetime.combine(date(2024, 11, 5), datetime.min.time())),
            requested_duration=60,  # 60 minutes
            status='Allocated'
        )

        lesson_requests, total = generate_invoice(self.invoice, term_start, term_end)

        # Ensure only the first lesson request is within the term
        self.assertIn(lesson_request_1, lesson_requests)
        self.assertNotIn(lesson_request_2, lesson_requests)

        # Check the total price is calculated correctly for the lesson in the range
        expected_total = (90 / 60) * settings.HOURLY_RATE
        self.assertEqual(total, expected_total)

    def test_generate_invoice_with_zero_total(self):
        """Test generate_invoice when no lesson requests match the term dates."""
        # Create an invoice with no lessons
        new_invoice = Invoice.objects.create(
            student=self.student,
            invoice_num='INV12346',
            due_date=timezone.make_aware(datetime.combine(date(2024, 12, 31), datetime.min.time())),  # Convert and make aware
            payment_status='Unpaid'
        )

        term_start = timezone.make_aware(datetime.combine(date(2024, 6, 1), datetime.min.time()))  # Convert and make aware
        term_end = timezone.make_aware(datetime.combine(date(2024, 8, 31), datetime.min.time()))  # Convert and make aware

        # Generate invoice with term dates, but no lessons
        lesson_requests, total = generate_invoice(new_invoice, term_start, term_end)

        # No lesson requests should be found
        self.assertEqual(len(lesson_requests), 0)

        # Ensure the total is 0 and the payment status is 'Paid'
        self.assertEqual(total, 0)
        self.assertEqual(new_invoice.payment_status, 'Paid')

    def test_generate_invoice_multiple_lessons(self):
        """Test generate_invoice with multiple lessons within a term."""
        term_start = timezone.make_aware(datetime.combine(date(2024, 9, 1), datetime.min.time()))
        term_end = timezone.make_aware(datetime.combine(date(2024, 12, 31), datetime.min.time()))

        # Add multiple lesson requests within the term
        lesson_request_1 = LessonRequest.objects.create(
            student=self.student,
            request_date=timezone.make_aware(datetime.combine(date(2024, 9, 15), datetime.min.time())),
            requested_duration=90,  # 90 minutes
            status='Allocated'
        )

        lesson_request_2 = LessonRequest.objects.create(
            student=self.student,
            request_date=timezone.make_aware(datetime.combine(date(2024, 10, 15), datetime.min.time())),
            requested_duration=60,  # 60 minutes
            status='Allocated'
        )

        lesson_request_3 = LessonRequest.objects.create(
            student=self.student,
            request_date=timezone.make_aware(datetime.combine(date(2024, 11, 5), datetime.min.time())),
            requested_duration=120,  # 120 minutes
            status='Allocated'
        )

        lesson_requests, total = generate_invoice(self.invoice, term_start, term_end)

        # Ensure all lesson requests are found within the term
        self.assertEqual(len(lesson_requests), 3)

        # Calculate the total for all lesson requests (90 + 60 + 120 = 270 minutes = 4.5 hours)
        expected_total = (90 + 60 + 120) / 60 * settings.HOURLY_RATE
        self.assertEqual(total, expected_total)
