from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from tutorials.models import LessonRequest, Invoice, User
from django.conf import settings 
from datetime import date
from tutorials.views import generate_invoice
from django.contrib.auth import get_user_model

class GenerateInvoiceTest(TestCase):

    @patch('code_tutors.settings.HOURLY_RATE', 20)

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.com',
            password='password123',
            role='student'
        )
        self.invoice = Invoice.objects.create(
            student_id=1,
            due_date=date(2024, 12, 15)
            )
        self.lesson1 = LessonRequest.objects.create(
            student=self.invoice.student,
            requested_duration=60,  
            request_date=date(2024, 12, 1),
            status='Allocated'
        )
        self.lesson2 = LessonRequest.objects.create(
            student=self.invoice.student,
            requested_duration=120,  
            request_date=date(2025, 2, 5),
            status='Allocated'
        )
        self.other_lesson = LessonRequest.objects.create(
            student=self.invoice.student,
            requested_duration=90,  
            request_date=date(2025, 7, 5),
            status='Completed' 
        )

    def test_generate_invoice_no_date_range(self):
        lesson_requests, total = generate_invoice(self.invoice)

        self.assertEqual(len(lesson_requests), 2)
        self.assertIn(self.lesson1, lesson_requests)
        self.assertIn(self.lesson2, lesson_requests)
        self.assertNotIn(self.other_lesson, lesson_requests)

        self.assertEqual(total, 50 + 100)  

    def test_generate_invoice_with_date_range(self):
        term_start = date(2024, 12, 1)
        term_end = date(2024, 12, 3)

        lesson_requests, total = generate_invoice(self.invoice, term_start, term_end)

        self.assertEqual(len(lesson_requests), 1)
        self.assertIn(self.lesson1, lesson_requests)
        self.assertNotIn(self.lesson2, lesson_requests)
        self.assertNotIn(self.other_lesson, lesson_requests)

        self.assertEqual(total, 50)  

    def test_generate_invoice_no_matching_requests(self):
        term_start = date(2024, 1, 1)
        term_end = date(2024, 1, 31)

        lesson_requests, total = generate_invoice(self.invoice, term_start, term_end)

        self.assertEqual(len(lesson_requests), 0)
        self.assertEqual(total, 0)
