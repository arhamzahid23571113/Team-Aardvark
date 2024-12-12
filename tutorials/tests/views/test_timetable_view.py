from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest

User = get_user_model()

class TutorTimetableTestCase(TestCase):
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]
    def setUp(self):
        # Create a tutor user
        self.tutor_user = User.objects.get(
            username='@janedoe'
        )

        # Create a student user
        self.student_user = User.objects.get(
            username='@petrapickles'
        )

        # Create lesson requests
        self.lesson_request = LessonRequest.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            requested_date=date.today(),
            requested_time=time(10, 0),
            requested_duration=60,
            requested_topic="Math Lesson",
            status='Allocated'
        )

        self.client = Client()

    def test_redirect_if_not_authenticated(self):
        response = self.client.get(reverse('student_timetable'))
        self.assertRedirects(response, reverse('log_in'))

    def test_redirect_if_not_tutor(self):
        self.client.login(username='@petrapickles', password='Password123')
        response = self.client.get(reverse('student_timetable'))
        self.assertRedirects(response, reverse('log_in'))

    def test_timetable_display(self):
        self.client.login(username='@janedoe', password='Password123')

        response = self.client.get(reverse('tutor_timetable'), {
            'year': date.today().year,
            'month': date.today().month
        })

    
        self.assertTemplateUsed(response, 'tutor_timetable.html')

        # Check context data
        self.assertIn('month_name', response.context)
        self.assertIn('year', response.context)
        self.assertIn('month_days', response.context)

        # Check lessons in context
        month_days = response.context['month_days']
        today = date.today()

        found_today = False
        for week in month_days:
            for day in week:
                if day['date'] == today:
                    found_today = True
                    self.assertEqual(len(day['lessons']), 1)
                    lesson = day['lessons'][0]
                    self.assertEqual(lesson['notes'], "Math Lesson")
                    self.assertEqual(lesson['student'], f"{self.student_user.first_name} {self.student_user.last_name}")

        self.assertTrue(found_today)