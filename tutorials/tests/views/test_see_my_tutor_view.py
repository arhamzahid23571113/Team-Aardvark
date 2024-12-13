from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest

User = get_user_model()

class SeeMyTutorViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create student and tutor users
        self.student = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='Password123',
            role='student'
        )
        self.tutor = User.objects.create_user(
            username='tutor1',
            email='tutor1@example.com',
            password='Password123',
            role='tutor'
        )

        # Create allocated lesson request
        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            tutor=self.tutor,
            status='Allocated',
            requested_topic='Ruby on Rails',
            requested_date='2024-01-01',
            requested_time='10:00:00',
            requested_duration=60
        )

        # Create a lesson request that is not allocated
        self.unallocated_lesson_request = LessonRequest.objects.create(
            student=self.student,
            tutor=None,
            status='Unallocated',
            requested_topic='Python Programming',
            requested_date='2024-01-02',
            requested_time='11:00:00',
            requested_duration=60
        )

        # URL for the view
        self.url = reverse('my_tutor_profile')

    def test_redirect_if_not_authenticated(self):
     """Test that unauthenticated users are redirected to the login page."""
     response = self.client.get(self.url)
     self.assertEqual(response.status_code, 302)
     self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")
     

    def test_tutor_list_displayed(self):
        """Test that the view displays a list of allocated tutors for the student."""
        self.client.login(username='student1', password='Password123')  # Student login
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_tutor_profile.html')

        # Ensure only allocated tutors are displayed
        tutors = response.context['tutors']
        self.assertEqual(len(tutors), 1)
        self.assertEqual(tutors[0]['tutor__id'], self.tutor.id)
        self.assertEqual(tutors[0]['tutor__first_name'], self.tutor.first_name)
        self.assertEqual(tutors[0]['tutor__last_name'], self.tutor.last_name)
        self.assertEqual(tutors[0]['tutor__email'], self.tutor.email)

    def test_no_tutors_displayed(self):
        """Test that no tutors are displayed if the student has no allocated tutors."""
        # Create a new student with no allocated tutors
        student2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='Password123',
            role='student'
        )
        self.client.login(username='student2', password='Password123')  # New student login
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_tutor_profile.html')

        # Ensure no tutors are displayed
        tutors = response.context['tutors']
        self.assertEqual(len(tutors), 0)

