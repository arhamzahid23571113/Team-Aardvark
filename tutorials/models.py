from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.conf import settings


class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )

    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    ROLES = (
        ('admin', 'Admin'),
        ('tutor', 'Tutor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='student')

    expertise = models.TextField(blank=True, null=True,
                                 help_text="Comma-separated list of programming languages or topics the tutor specializes in.")

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

class Invoice(models.Model):
    """Model for invoices and tracking payment status"""
    student = models.ForeignKey(User, related_name="invoices",on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=8, decimal_places=2)
    due_date = models.DateField()
    payment_status = models.CharField(max_length=20, choices=[('Paid', 'Paid'),('Unpaid', 'Unpaid')])
    invoice_date = models.DateField(auto_now_add=True)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Invoice for {self.student.first_name} {self.student.last_name}"
    

class LessonRequest(models.Model):
    """Model for students to request lessons"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="lesson_requests",
        on_delete=models.CASCADE,
        help_text="The student making the lesson request."
    )
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_requests",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The tutor assigned to this lesson request. Null if unallocated."
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('Unallocated', 'Unallocated'),
            ('Allocated', 'Allocated'),
            ('Pending', 'Pending'),
            ('Cancelled', 'Cancelled')
        ],
        default='Unallocated',
        help_text="The current status of the lesson request."
    )
    request_date = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the lesson request was created."
    )
    requested_topic = models.TextField(
        blank=True,
        help_text="Describe what you would like to learn (e.g Web Development with Django)."
    )
    requested_frequency = models.CharField(
        max_length=20,
        help_text="How often would you like your lessons (e.g Weekly, Fortnightly)?"
    )
    requested_duration = models.PositiveIntegerField(
        help_text="Lesson duration in minutes."
    )
    requested_time = models.TimeField(
        help_text="Preferred time for the lesson."
    )
    experience_level = models.TextField(
        help_text="Describe your level of experience with this topic."
    )
    additional_notes = models.TextField(
        blank=True,
        help_text="Additional information or requests."
    )

    class Meta:
        verbose_name = "Lesson Request"
        verbose_name_plural = "Lesson Requests"
        ordering = ['-request_date']

    def __str__(self):
        return f"Lesson Request by {self.student.full_name} for {self.requested_topic}"

class LessonBooking(models.Model):
    """Models used for showing lesson bookings between students and tutors"""

    # Relationships
    student = models.ForeignKey(User, related_name="student_lessons", on_delete=models.CASCADE)
    tutor = models.ForeignKey(User, related_name="tutor_lessons", on_delete=models.CASCADE)

    # Fields matching the template
    topic = models.CharField(max_length=100)  # Use CharField for the dropdown of topics
    duration = models.CharField(max_length=20)  # Duration as string (e.g., "30 Minutes")
    time = models.TimeField()  # Time input for preferred time
    lesson_date = models.DateField()  # Placeholder for the actual date

    # New fields from the template
    frequency = models.CharField(max_length=20)  # Weekly/Fortnightly
    preferred_day = models.CharField(max_length=10)  # Dropdown of weekdays
    experience_level = models.CharField(max_length=20)  # No Experience/Beginner/Intermediate/Advanced
    additional_notes = models.TextField(blank=True, null=True)  # Additional Notes

    def __str__(self):
        return f"{self.student.username} - {self.topic} with {self.tutor.username}"