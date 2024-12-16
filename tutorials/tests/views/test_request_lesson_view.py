from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest
from tutorials.forms import LessonBookingForm

User = get_user_model()

class RequestLessonTestCase(TestCase):
    def setUp(self):
        """Set up a student user and test data."""
        self.student_user = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="Password123",
            role="student"
        )
        self.valid_form_data = {
            'requested_topic': 'python_programming',  
            'requested_date': '2024-01-01',
            'requested_time': '10:00:00',
            'requested_duration': 90,
            'requested_frequency': 'weekly',
            'experience_level': 'beginner',
            'additional_notes': 'I would like help with advanced topics.'
        }
        self.invalid_form_data = {
            'requested_topic': 'Invalid Topic',
            'requested_date': 'invalid-date',
            'requested_time': '',
            'requested_duration': -1
        }
        self.conflicting_request = LessonRequest.objects.create(
            student=self.student_user,
            requested_topic='python_programming',
            requested_date='2024-01-01',
            requested_time='10:00:00',
            requested_duration=90,
            status='Allocated'
        )

    def test_get_request_lesson(self):
        """Test GET request to render the lesson booking form."""
        self.client.login(username="student1", password="Password123")
        response = self.client.get(reverse('request_lesson'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_lesson.html')
        self.assertIsInstance(response.context['form'], LessonBookingForm)

    def test_post_valid_form(self):
        """Test POST request with valid form data."""
        self.client.login(username="student1", password="Password123")
        response = self.client.post(reverse('request_lesson'), data=self.valid_form_data)
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, reverse('lesson_request_success'))
        self.assertEqual(LessonRequest.objects.count(), 2)  

    def test_post_invalid_form(self):
        """Test POST request with invalid form data."""
        self.client.login(username="student1", password="Password123")
        response = self.client.post(reverse('request_lesson'), data=self.invalid_form_data)
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'request_lesson.html')
        self.assertContains(response, 'Enter a valid date.')
        self.assertContains(response, 'Select a valid choice.')
        self.assertEqual(LessonRequest.objects.count(), 1)  

    def test_post_no_data(self):
        """Test POST request with no data submitted."""
        self.client.login(username="student1", password="Password123")
        response = self.client.post(reverse('request_lesson'), data={})
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'request_lesson.html')
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'requested_date', 'This field is required.')
        self.assertEqual(LessonRequest.objects.count(), 1)  

    def test_post_conflicting_request(self):
        """Test POST request with a conflicting lesson request."""
        self.client.login(username="student1", password="Password123")
        conflicting_form_data = {
            'requested_topic': 'python_programming',
            'requested_date': '2024-01-01',
            'requested_time': '10:30:00',  
            'requested_duration': 60,
            'requested_frequency': 'weekly',
            'experience_level': 'beginner',
            'additional_notes': 'Conflict test'
        }
        response = self.client.post(reverse('request_lesson'), data=conflicting_form_data)
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'request_lesson.html')
        self.assertContains(response, "A lesson has already been booked for this time and date.")
        self.assertEqual(LessonRequest.objects.count(), 1) 
