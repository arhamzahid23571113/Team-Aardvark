"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, LessonRequest,ContactMessage

from .models import User, LessonRequest,ContactMessage

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

def validate_file_size(value):
    """Validator to ensure profile picture file size does not exceed 10 MB."""
    max_size = 10 * 1024 * 1024  
    if value.size > max_size:
        raise ValidationError("Profile picture size cannot exceed 10 MB.")

class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'profile_picture', 'expertise']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            if user.role == 'student':
                self.fields.pop('role', None)
                self.fields.pop('expertise', None)
            elif user.role == 'tutor':
                self.fields.pop('role', None)
            elif user.role == 'admin':
                self.fields.pop('expertise', None)

    def clean_profile_picture(self):
        """Validate the profile picture file size."""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            validate_file_size(profile_picture)
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

class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self.user = user
        if not user:
            raise ValueError("A valid user must be provided.")

    def clean(self):
        super().clean()
        password = self.cleaned_data.get('password')
        if self.user and not authenticate(username=self.user.username, password=password):
            self.add_error('password', "Password is invalid")

    def save(self):
        new_password = self.cleaned_data['new_password']
        if self.user:
            self.user.set_password(new_password)
            self.user.save()
        return self.user

class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']

    def save(self, commit=True):
        if not self.is_valid():
            raise ValueError("The form contains invalid data.")
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            role=self.cleaned_data.get('role'),
        )

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