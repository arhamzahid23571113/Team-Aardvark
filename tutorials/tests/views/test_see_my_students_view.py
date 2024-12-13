from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest

User = get_user_model()

class SeeMyStudentsProfileViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create tutor and student users
        self.tutor = User.objects.create_user(
            username='tutor1',
            email='tutor1@example.com',
            password='Password123',
            role='tutor'
        )
        self.student1 = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='Password123',
            role='student'
        )
        self.student2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='Password123',
            role='student'
        )

        # Create lesson requests
        self.lesson_request1 = LessonRequest.objects.create(
            student=self.student1,
            tutor=self.tutor,
            status='Allocated',
            requested_topic='Python Progamming',
            requested_date='2024-01-01',
            requested_time='10:00:00',
            requested_duration=60
        )
        self.lesson_request2 = LessonRequest.objects.create(
            student=self.student2,
            tutor=self.tutor,
            status='Allocated',
            requested_topic='ReactJS',
            requested_date='2024-01-02',
            requested_time='11:00:00',
            requested_duration=90
        )
        self.unallocated_request = LessonRequest.objects.create(
            student=self.student2,
            tutor=None,
            status='Unallocated',
            requested_topic='Python Basics',
            requested_date='2024-01-03',
            requested_time='12:00:00',
            requested_duration=45
        )

        # URL for the view
        self.url = reverse('my_students_profile')

    def test_redirect_if_not_authenticated(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")


    def test_assigned_students_displayed(self):
        """Test that the view displays the assigned students for the tutor."""
        self.client.login(username='tutor1', password='Password123')  # Tutor login
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_students_profile.html')

        # Ensure only students with allocated lessons are displayed
        students = response.context['students']
        self.assertEqual(len(students), 2)
        self.assertIn(self.student1, students)
        self.assertIn(self.student2, students)

    def test_no_students_displayed(self):
        """Test that no students are displayed if the tutor has no assigned students."""
        # Create a new tutor with no assigned students
        tutor2 = User.objects.create_user(
            username='tutor2',
            email='tutor2@example.com',
            password='Password123',
            role='tutor'
        )

        self.client.login(username='tutor2', password='Password123')  # New tutor login
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_students_profile.html')

        # Ensure no students are displayed
        students = response.context['students']
        self.assertEqual(len(students), 0)

