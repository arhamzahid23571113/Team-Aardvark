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
            'requested_topic': 'Python Programming',  # Must match a valid dropdown choice
            'requested_date': '2024-01-01',
            'requested_time': '10:00:00',
            'requested_duration': 90,
            'requested_frequency': 'Weekly',  # Must match a valid dropdown choice
            'experience_level': 'Beginner',  # Must match a valid dropdown choice if applicable
            'additional_notes': 'I would like help with advanced topics.'
        }
        self.invalid_form_data = {
            'requested_topic': 'Invalid Topic',  # Not in dropdown choices
            'requested_date': 'invalid-date',  # Invalid date format
            'requested_time': '',  # Missing time
            'requested_duration': -1  # Invalid duration
        }

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
        self.assertEqual(response.status_code, 302)  # Redirect to success page
        self.assertRedirects(response, reverse('lesson_request_success'))
        self.assertEqual(LessonRequest.objects.count(), 1)  # Ensure a LessonRequest was created
        lesson_request = LessonRequest.objects.first()
        self.assertEqual(lesson_request.student, self.student_user)
        self.assertEqual(lesson_request.requested_topic, 'Python Programming')
        self.assertEqual(lesson_request.requested_duration, 90)

    def test_post_invalid_form(self):
        """Test POST request with invalid form data."""
        self.client.login(username="student1", password="Password123")
        response = self.client.post(reverse('request_lesson'), data=self.invalid_form_data)
        self.assertEqual(response.status_code, 200)  # Stay on the same page
        self.assertTemplateUsed(response, 'request_lesson.html')
        self.assertContains(response, 'Enter a valid date.')  # Specific error message for invalid date
        self.assertContains(response, 'Ensure this value is greater than or equal to 0.')  # For duration
        self.assertEqual(LessonRequest.objects.count(), 0)  # No LessonRequest should be created

    def test_post_no_data(self):
        """Test POST request with no data submitted."""
        self.client.login(username="student1", password="Password123")
        response = self.client.post(reverse('request_lesson'), data={})
        self.assertEqual(response.status_code, 200)  # Stay on the same page
        self.assertTemplateUsed(response, 'request_lesson.html')
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'requested_date', 'This field is required.')  # Specific field error
        self.assertEqual(LessonRequest.objects.count(), 0)

