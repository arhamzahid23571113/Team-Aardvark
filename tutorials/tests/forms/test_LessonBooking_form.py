from django.test import TestCase
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from tutorials.forms import LessonBookingForm
from tutorials.models import LessonRequest, User

class LessonBookingFormTestCase(TestCase):
    def setUp(self):
        self.tutor = User.objects.create(username="tutor1", role="tutor", email="tutor1@example.com")
        self.student = User.objects.create(username="student1", role="student", email="student1@example.com")
        
        # Pre-existing lesson request to simulate a conflict
        LessonRequest.objects.create(
            student=self.student,
            tutor=self.tutor,
            requested_date="2024-12-20",
            requested_time="10:00",
            requested_duration=60,
            requested_topic="python_programming",
            status="Allocated",
        )

        self.valid_data = {
            "requested_topic": "python_programming",
            "requested_frequency": "weekly",
            "requested_duration": 60,
            "requested_time": "10:00",
            "requested_date": "2024-12-20",
            "experience_level": "beginner",
            "additional_notes": "",
        }

    def test_form_valid_with_correct_data(self):
        """Test that the form is valid when all fields are filled correctly."""
        form = LessonBookingForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["requested_topic"], "python_programming")
        self.assertEqual(form.cleaned_data["requested_frequency"], "weekly")
        self.assertEqual(form.cleaned_data["requested_duration"], 60)
        self.assertEqual(form.cleaned_data["additional_notes"], "")
        if not form.is_valid():
            print("Form errors:", form.errors)  
        self.assertTrue(form.is_valid())  

    def test_form_invalid_missing_required_fields(self):
        """Test that the form is invalid if required fields are missing."""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("requested_topic") 
        form = LessonBookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("requested_topic", form.errors)  

    def test_form_invalid_with_invalid_date_format(self):
        """Test that the form is invalid if the date format is incorrect."""
        invalid_data = self.valid_data.copy()
        invalid_data["requested_date"] = "20-12-2024"  
        form = LessonBookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("requested_date", form.errors)

    def test_form_invalid_with_invalid_choice_for_dropdown(self):
        """Test that the form is invalid if an invalid choice is selected for a dropdown field."""
        invalid_data = self.valid_data.copy()
        invalid_data["requested_topic"] = "invalid_topic"  
        form = LessonBookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("requested_topic", form.errors)

    def test_form_invalid_with_empty_duration(self):
        """Test that the form is invalid if requested_duration is empty."""
        invalid_data = self.valid_data.copy()
        invalid_data["requested_duration"] = "" 
        form = LessonBookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("requested_duration", form.errors)

    def test_form_invalid_with_invalid_time_format(self):
        """Test that the form is invalid if requested_time has an incorrect format."""
        invalid_data = self.valid_data.copy()
        invalid_data["requested_time"] = "25:00"  
        form = LessonBookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("requested_time", form.errors)

    def test_form_valid_with_boundary_duration_choice(self):
        """Test that the form is valid with boundary values for requested_duration."""
        for duration in ["30", "60", "90", "120"]:  # Use strings for dropdown values
            valid_data = self.valid_data.copy()
            valid_data["requested_duration"] = duration
            form = LessonBookingForm(data=valid_data)
            self.assertTrue(form.is_valid(), msg=f"Form failed with duration: {duration}. Errors: {form.errors}")

    def test_form_valid_without_conflict(self):
        """Test that the form is valid when no scheduling conflict exists."""
        valid_data = self.valid_data.copy()
        valid_data["requested_time"] = "11:00"  # No conflict with existing lesson
        form = LessonBookingForm(data=valid_data)
        form.instance.tutor = self.tutor  # Assign tutor for conflict validation
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_time_conflict(self):
        """Test that the form is invalid if a scheduling conflict exists."""
        form = LessonBookingForm(data=self.valid_data)
        form.instance.tutor = self.tutor  # Assign tutor for conflict validation
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)  # Check for non-field error in form-wide validation
        self.assertEqual(
            form.errors["__all__"][0],
            "This tutor is already booked at the requested time on 2024-12-20."
        )

    def test_form_valid_with_different_tutor(self):
        """Test that the form is valid when the tutor is different, even if the time conflicts."""
        another_tutor = User.objects.create(username="tutor2", role="tutor", email="tutor2@example.com")
        form = LessonBookingForm(data=self.valid_data)
        form.instance.tutor = another_tutor  # Assign a different tutor
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_partial_overlap(self):
        """Test that the form is invalid if the requested time partially overlaps with an existing lesson."""
        partial_overlap_data = self.valid_data.copy()
        partial_overlap_data["requested_time"] = "09:30"  # Overlaps with 10:00-11:00
        form = LessonBookingForm(data=partial_overlap_data)
        form.instance.tutor = self.tutor
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_form_valid_with_non_overlapping_time(self):
        """Test that the form is valid if the requested time is adjacent but does not overlap."""
        non_overlapping_data = self.valid_data.copy()
        non_overlapping_data["requested_time"] = "11:00"  # Adjacent to 10:00-11:00 but no overlap
        form = LessonBookingForm(data=non_overlapping_data)
        form.instance.tutor = self.tutor
        self.assertTrue(form.is_valid())
