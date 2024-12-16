from django.test import TestCase
from django.core.exceptions import ValidationError
from tutorials.models import LessonRequest, User
from datetime import time, date, timedelta


class LessonRequestModelTest(TestCase):
    def setUp(self):
        """Create two test users for the lesson requests."""
        self.student1 = User.objects.create_user(
            username='@student1', email='student1@example.com', password='password', role='student'
        )
        self.student2 = User.objects.create_user(
            username='@student2', email='student2@example.com', password='password', role='student'
        )

    def test_no_overlap_allowed(self):
        """Test that overlapping lesson requests raise a ValidationError."""
        # Create the first lesson request
        LessonRequest.objects.create(
            student=self.student1,
            requested_date=date(2024, 1, 1),
            requested_time=time(10, 0),
            requested_duration=timedelta(minutes=60),  # 1 hour
            status='Allocated'
        )

        # Attempt to create an overlapping lesson request
        overlapping_request = LessonRequest(
            student=self.student2,
            requested_date=date(2024, 1, 1),
            requested_time=time(10, 30),  # Starts during the existing lesson
            requested_duration=timedelta(minutes=60)
        )
        with self.assertRaises(ValidationError):
            overlapping_request.clean()

    def test_no_error_for_non_overlapping_requests(self):
        """Test that non-overlapping lesson requests do not raise a ValidationError."""
        # Create the first lesson request
        LessonRequest.objects.create(
            student=self.student1,
            requested_date=date(2024, 1, 1),
            requested_time=time(10, 0),
            requested_duration=timedelta(minutes=60),  # 1 hour
            status='Allocated'
        )

        # Create a non-overlapping lesson request
        non_overlapping_request = LessonRequest(
            student=self.student2,
            requested_date=date(2024, 1, 1),
            requested_time=time(11, 0),  # Starts after the previous lesson ends
            requested_duration=timedelta(minutes=60)
        )
        try:
            non_overlapping_request.clean()
        except ValidationError:
            self.fail("ValidationError raised for non-overlapping request.")