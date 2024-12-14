from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest

User = get_user_model()


class TutorMoreInfoViewTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="Password123",
            role="student"
        )
        
        self.tutor = User.objects.create_user(
            username="tutor122",
            email="tutor122@example.com",
            password="Password123",
            role="tutor"
        )
        
        self.unrelated_tutor = User.objects.create_user(
            username="tutor222",
            email="tutor222@example.com",
            password="Password123",
            role="tutor"
        )
        
        self.lesson = LessonRequest.objects.create(
            student=self.student,
            tutor=self.tutor,
            status="Allocated",
            requested_topic="Python Programming",
            requested_date="2024-01-01",
            requested_time="10:00:00",
            requested_duration=60
        )
        
        self.url = reverse("tutor_more_info", args=[self.tutor.id])

    def test_student_access_tutor_more_info(self):
        """Test that a student can access the tutor_more_info page."""
        self.client.login(username="student1", password="Password123")
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor_more_info.html")
        
        self.assertEqual(response.context["tutor"], self.tutor)
        lessons = response.context["lessons"]
        self.assertEqual(len(lessons), 1)
        self.assertIn(self.lesson, lessons)


    def test_non_student_cannot_access_tutor_more_info(self):
        """Test that a non-student user cannot access the tutor_more_info page."""
        tutor_login = self.client.login(username="tutor1", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"{reverse('log_in')}?next={self.url}"
        )

    def test_invalid_tutor_id_raises_404(self):
        """Test that accessing a non-existent tutor ID raises a 404 error."""
        self.client.login(username="student1", password="Password123")
        invalid_url = reverse("tutor_more_info", args=[999])  
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
