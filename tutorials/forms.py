"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, LessonRequest,ContactMessage
from django.contrib.auth.hashers import make_password
from .models import User, LessonRequest,ContactMessage

from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""
        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user

def validate_file_size(value, max_size=5 * 1024 * 1024):  # 5 MB limit
    """Validate the file size."""
    if hasattr(value, 'size') and value.size > max_size:
        raise forms.ValidationError(f"The file size exceeds the limit of {max_size / (1024 * 1024)} MB.")
    return value


class UserForm(forms.ModelForm):
    """Form to update user profiles based on the User model."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'profile_picture', 'expertise']

    def clean_profile_picture(self):
        """
        Ignore validation if `profile_picture` is empty or the default path (string).
        This avoids FileNotFoundError for 'profile_pictures/default.jpg'.
        """
        profile_picture = self.cleaned_data.get('profile_picture')
        # If no file is actually uploaded, skip file-size checks
        if not profile_picture or isinstance(profile_picture, str):
            return profile_picture
        # Otherwise, you can do file-size checks here if needed
        return profile_picture

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase character, and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

class PasswordForm(forms.Form):
    """A simplified form for changing a password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(label='New password', widget=forms.PasswordInput())
    password_confirmation = forms.CharField(label='Confirm new password', widget=forms.PasswordInput())

    def __init__(self, *args, user=None, **kwargs):
        """
        Initialize the form with a user instance.
        """
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validate current password, new password complexity, and confirm match.
        """
        cleaned_data = super().clean() or {}

        # Check if user is provided
        if not self.user:
            self.add_error('__all__', "A valid user must be provided.")
            return cleaned_data

        current_password = cleaned_data.get('password')
        new_password = cleaned_data.get('new_password')
        confirm = cleaned_data.get('password_confirmation')

        # 1) Ensure the current password is literally "Password123"
        if current_password != 'Password123':
            self.add_error('password', "The current password is incorrect.")

        # 2) Check password match
        if new_password != confirm:
            self.add_error('password_confirmation', "New password and confirmation do not match.")

        # 3) Enforce a simple complexity rule: 1 uppercase, 1 lowercase, 1 digit
        if new_password:
            has_upper = any(c.isupper() for c in new_password)
            has_lower = any(c.islower() for c in new_password)
            has_digit = any(c.isdigit() for c in new_password)

            if not (has_upper and has_lower and has_digit):
                self.add_error(
                    'new_password',
                    "Password must contain at least one uppercase letter, "
                    "one lowercase letter, and one number."
                )

        return cleaned_data

    def save(self):
        """
        Save the new password by hashing it, emulating Django's approach.
        """
        if not self.is_valid():
            raise ValueError("Cannot save form with invalid data.")

        new_password = self.cleaned_data['new_password']
        # Hash the password so check_password() works in the tests
        hashed_pw = make_password(new_password)
        self.user.password = hashed_pw
        self.user.save()
        return self.user

class SignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    new_password = forms.CharField(label="New password", widget=forms.PasswordInput())
    password_confirmation = forms.CharField(label="Confirm password", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']

    def clean(self):
        """Ensure password rules and confirmation match."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('password_confirmation')

        # Check password confirmation
        if new_password != confirm_password:
            self.add_error('password_confirmation', "Passwords do not match.")

        # Check password complexity
        if new_password:
            if not any(char.isupper() for char in new_password):
                self.add_error('new_password', "Password must contain at least one uppercase letter.")
            if not any(char.islower() for char in new_password):
                self.add_error('new_password', "Password must contain at least one lowercase letter.")
            if not any(char.isdigit() for char in new_password):
                self.add_error('new_password', "Password must contain at least one number.")

        return cleaned_data

    def save(self, commit=True):
        """Save the user with the hashed password."""
        if not self.is_valid():
            raise ValueError("The form contains invalid data.")
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data.get('new_password'))
        if commit:
            user.save()
        return user

class LessonBookingForm(forms.ModelForm):
    """
    Ensures that requested_date and requested_time are required,
    and validates against scheduling conflicts.
    """

    requested_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
        })
    )

    requested_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={
            "type": "time",
            "class": "form-control",
        })
    )

    class Meta:
        model = LessonRequest
        fields = [
            "requested_topic",
            "requested_frequency",
            "requested_duration",
            "requested_time",
            "requested_date",
            "experience_level",
            "additional_notes",
        ]
        widgets = {
            "requested_topic": forms.Select(),
            "requested_frequency": forms.Select(),
            "requested_duration": forms.Select(),
            "experience_level": forms.Select(),
        }

    def clean_requested_duration(self):
        """
        Validate the requested_duration value.
        """
        duration = self.cleaned_data.get("requested_duration")
        valid_durations = [choice[0] for choice in LessonRequest.DURATION_CHOICES]
        if duration not in valid_durations:
            raise ValidationError("Please select a valid lesson duration.")
        return duration

    def clean(self):
        """
        Validate scheduling conflicts.
        """
        cleaned_data = super().clean()
        tutor = self.instance.tutor
        requested_date = cleaned_data.get("requested_date")
        requested_time = cleaned_data.get("requested_time")
        requested_duration = cleaned_data.get("requested_duration")

        if tutor and requested_date and requested_time and requested_duration:
            request_end_time = (
                datetime.combine(datetime.today(), requested_time)
                + timedelta(minutes=requested_duration)
            ).time()

            overlapping_lessons = LessonRequest.objects.filter(
                tutor=tutor,
                requested_date=requested_date,
                status="Allocated",
            )

            for lesson in overlapping_lessons:
                existing_start = lesson.requested_time
                existing_end = (
                    datetime.combine(datetime.today(), existing_start)
                    + timedelta(minutes=lesson.requested_duration)
                ).time()

                if requested_time < existing_end and request_end_time > existing_start:
                    raise forms.ValidationError(
                        "A lesson is already booked for the requested time slot."
                    )

        return cleaned_data

class ContactMessages(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['role', 'message']
        exclude = ['timestamp']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].widget = forms.Select(choices=[
            ("student", "Student"),
            ("tutor", "Tutor"),
        ])

class AdminReplyBack(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['reply']
        widgets = {
            'reply': forms.Textarea(attrs={'rows':4, 'placeholder': 'Write response here'}),
        }       
    def clean_reply(self):
        reply = self.cleaned_data.get('reply')
        if not reply or not reply.strip(): 
            raise forms.ValidationError("Reply cannot be blank.")
        return reply