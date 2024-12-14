from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.conf import settings

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

    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        default='profile_pictures/default.jpg', 
        blank=True
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        if self.profile_picture and self.profile_picture.name != 'profile_pictures/default.jpg':
            return self.profile_picture.url
        gravatar_object = Gravatar(self.email)
        return gravatar_object.get_image(size=size, default='mp')

    def mini_gravatar(self):
        return self.gravatar(size=60)

class Invoice(models.Model):
    """Model for invoices and tracking payment status"""
    student = models.ForeignKey(
        User,
        related_name="invoices",  # Unique related_name for Invoice
        on_delete=models.CASCADE
    )
    amount_due = models.DecimalField(max_digits=8, decimal_places=2)
    due_date = models.DateField()
    payment_status = models.CharField(
        max_length=20,
        choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')]
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')]
    )
    invoice_date = models.DateField(auto_now_add=True)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Invoice for {self.student.first_name} {self.student.last_name}"

class LessonRequest(models.Model):
    """Model for students to make request lessons"""
    TOPIC_CHOICES = [
        ("python_programming", "Python Programming"),
        ("web_development_with_js", "Web Development with JavaScript"),
        ("ruby_on_rails", "Ruby on Rails"),
        ("ai_and_ml", "AI and Machine Learning"),
    ]

    FREQUENCY_CHOICES = [
        ("weekly", "Weekly"),
        ("fortnightly", "Fortnightly"),
    ]

    DURATION_CHOICES = [
        (30, "30 Minutes"),
        (60, "1 Hour"),
        (90, "1 Hour and 30 Minutes"),
        (120, "2 Hours"),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ("no_experience", "No Experience"),
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
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
        default="Python Programming",
        choices=TOPIC_CHOICES,  
        help_text="Describe what you would like to learn (e.g Web Development with Django)."

    )
    requested_date = models.DateField(
        default="2024-01-01",
        help_text="Select the date for your lesson."
    )
    requested_frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default="Weekly",  
        help_text="How often would you like your lessons (e.g Weekly, Fortnightly)?"
    )

    requested_duration = models.PositiveIntegerField(
        default=60,
        choices=DURATION_CHOICES,  
        help_text="Lesson duration in minutes."
    )
    requested_time = models.TimeField(
        default="09:00:00",  
        help_text="Preferred time for the lesson."
    )
    experience_level = models.TextField(
        default="No Experience",
        choices=EXPERIENCE_LEVEL_CHOICES,  
        help_text="Describe your level of experience with this topic."
    )
    additional_notes = models.TextField(
        blank=True,
        default="",  
        help_text="Additional information or requests."
    )

    class Meta:
        verbose_name = "Lesson Request"
        verbose_name_plural = "Lesson Requests"
        ordering = ['-request_date']

    def __str__(self):
        return f"Lesson Request by {self.student.username} for {self.requested_topic}"

    class Meta:
        verbose_name = "Lesson Request"
        verbose_name_plural = "Lesson Requests"
        ordering = ['-request_date']

    def __str__(self):
        return f"Lesson Request by {self.student.username} for {self.requested_topic}"
    
       
class ContactMessage(models.Model):
    ROLES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices = ROLES)
    message = models.TextField(
        blank = True,
        default="",
        help_text="Write your message to the admin here"
    )
    reply = models.TextField(
        blank = True,
        null=True,
        default="",
        help_text="Admins reply to message"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_timestamp = models.DateTimeField(
    blank=True, null=True,
    help_text="Timestamp of admin's reply"
    )


    def __str__(self):
        return f"{self.role.capitalize()} - {self.timestamp}"
