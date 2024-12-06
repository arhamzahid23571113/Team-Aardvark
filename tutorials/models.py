from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.conf import settings

class User(AbstractUser):
    """Model used for user authentication, and team member-related information."""

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

    expertise = models.TextField(
        blank=True, null=True,
        help_text="Comma-separated list of programming languages or topics the tutor specializes in."
    )

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        return gravatar_object.get_image(size=size, default='mp')

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)




class Invoice(models.Model):
    """Model for invoices and tracking payment status"""
    student = models.ForeignKey(
        User,
        related_name="invoices",
        on_delete=models.CASCADE
    )
    amount_due = models.DecimalField(max_digits=8, decimal_places=2)
    due_date = models.DateField()
    payment_status = models.CharField(
        max_length=20,
        choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')]
    )
    invoice_date = models.DateField(auto_now_add=True)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Invoice for {self.student.user.full_name()}"


class LessonRequest(models.Model):
    """Model for students to request lessons"""
    student = models.ForeignKey(
        User,
        related_name="lesson_requests",
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('Unallocated', 'Unallocated'),
            ('Allocated', 'Allocated'),
            ('Pending', 'Pending'),
            ('Cancelled', 'Cancelled')
        ],
        default='Unallocated'
    )
    request_date = models.DateTimeField(auto_now_add=True)
    requested_topic = models.TextField(
        blank=True,
        help_text="Describe what you would like to learn (e.g Web Development with Django)"
    )
    requested_frequency = models.TextField(
        max_length=20,
        help_text="How often would you like your lessons (e.g Weekly, Fortnightly)?"
    )
    requested_duration = models.IntegerField(help_text="Lesson duration in minutes")
    requested_time = models.TimeField(help_text="Preferred time for the lesson")
    experience_level = models.TextField(
        help_text="Describe your level of experience with this topic."
    )
    additional_notes = models.TextField(
        blank=True,
        help_text="Additional information or requests"
    )


class LessonBooking(models.Model):
    student = models.ForeignKey(
        User,
        related_name="lesson_bookings_as_student",
        on_delete=models.CASCADE
    )
    tutor = models.ForeignKey(
        User,
        related_name="lesson_bookings_as_tutor",
        on_delete=models.CASCADE
    )
    topic = models.TextField(max_length=100)
    duration = models.IntegerField()
    time = models.TimeField()
    lesson_date = models.DateField()


class Lesson(models.Model):
    title = models.CharField(max_length=255, help_text="The title of the lesson")
    content = models.TextField(help_text="Content or description of the lesson")
    date = models.DateField(help_text="Date of the lesson")
    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lessons_as_tutor"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lessons_as_student"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Timetable(models.Model):
    tutor = models.ForeignKey(
        User,
        related_name="tutor_timetables",
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        User,
        related_name="student_timetables",
        on_delete=models.CASCADE
    )
    date = models.DateField(help_text="The date of the lesson")
    start_time = models.TimeField(help_text="Lesson start time")
    end_time = models.TimeField(help_text="Lesson end time")
    is_attended = models.BooleanField(
        default=False,
        help_text="Has the student attended this lesson?"
    )
    notes = models.TextField(
        blank=True, null=True,
        help_text="Additional notes about the lesson"
    )

    def __str__(self):
        return f"Lesson: {self.tutor.user.full_name()} teaching {self.student.user.full_name()} on {self.date}"
