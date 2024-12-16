from django.test import TestCase
from django.core.exceptions import ValidationError
from tutorials.models import LessonRequest, User
from datetime import time, date

class LessonRequestModelTest(TestCase):
    def setUp(self):
        self.student1 = User.objects.create_user(username='@student1', email='student1@example.com', password='password', role='student')
        self.student2 = User.objects.create_user(username='@student2', email='student2@example.com', password='password', role='student')

    def test_no_overlap_allowed(self):

        LessonRequest.objects.create(
            student=self.student1,
            requested_date=date(2024, 1, 1),
            requested_time=time(10, 0),
            requested_duration=60,
            status='Allocated'
        )

        with self.assertRaises(ValidationError):
            overlapping_request = LessonRequest(
                student=self.student2,
                requested_date=date(2024, 1, 1),
                requested_time=time(10, 30),  
                requested_duration=60
            )
            overlapping_request.clean()

    def test_no_error_for_non_overlapping_requests(self):

        LessonRequest.objects.create(
            student=self.student1,
            requested_date=date(2024, 1, 1),
            requested_time=time(10, 0),
            requested_duration=60,
            status='Allocated'
        )

        non_overlapping_request = LessonRequest(
            student=self.student2,
            requested_date=date(2024, 1, 1),
            requested_time=time(11, 0),  
            requested_duration=60
        )
        try:
            non_overlapping_request.clean()  
        except ValidationError:
            self.fail("ValidationError raised for non-overlapping request")
