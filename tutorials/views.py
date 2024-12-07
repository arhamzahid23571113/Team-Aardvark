from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.urls import reverse
from calendar import monthrange, SUNDAY
from datetime import date, datetime
from django.shortcuts import render
from datetime import datetime, date
import calendar
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from .models import User, Lesson, Timetable
from .models import Timetable

@login_required
def dashboard(request):
    """Redirect users to their role-based dashboards."""
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'tutor':
        return redirect('tutor_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    else:
        messages.error(request, "Invalid user role!")
        return redirect('home')

@login_prohibited
def home(request):
    """Display the application's start/home screen."""
    return render(request, 'home.html')

@login_required
def admin_dashboard(request):
    """Admin-specific dashboard."""
    return render(request, 'admin_dashboard.html')

@login_required
def tutor_dashboard(request):
    """Tutor-specific dashboard."""
    return render(request, 'tutor_dashboard.html')

@login_required
def student_dashboard(request):
    """Student-specific dashboard."""
    return render(request, 'student_dashboard.html')

def learn_more(request):
    """Display the Learn More page."""
    return render(request, 'learn_more.html')

def available_courses(request):
    """Display the Available Courses page."""
    return render(request, 'available_courses.html')

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""
    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        return self.redirect_when_logged_in_url

class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""
    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user:
            login(request, user)
            return redirect(self.next)
        messages.error(request, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})

def log_out(request):
    """Log out the current user."""
    logout(request)
    return redirect('home')

class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""
    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Password updated!")
        return reverse('dashboard')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen and handle profile modifications."""
    model = User
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, "Profile updated!")
        return reverse('dashboard')

class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""
    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard')

@login_required
def tutor_timetable(request):
    """View for tutors to see their timetable."""
    timetable = Timetable.objects.filter(tutor=request.user)
    return render(request, 'tutor_timetable.html', {'timetable': timetable})

@login_required
@login_required
@login_required
def timetable_view(request):
    """View for students and tutors to see their timetable in a calendar layout."""
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))

    # Calculate previous and next months
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Determine the first day of the month and its weekday
    first_day_of_month = date(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    empty_days = (first_day_of_month.weekday() + 1) % 7  # Adjust for Sunday start

    # Generate a range of empty days for template
    empty_days_range = range(empty_days)

    # Build a calendar structure
    month_days = []
    for week in calendar.Calendar(firstweekday=SUNDAY).monthdatescalendar(year, month):
        week_days = []
        for day in week:
            lessons = []
            if request.user.role == 'student':
                lessons = Timetable.objects.filter(student=request.user, date=day).order_by('start_time')
            elif request.user.role == 'tutor':
                lessons = Timetable.objects.filter(tutor=request.user, date=day).order_by('start_time')

            week_days.append({'date': day, 'lessons': lessons})
        month_days.append(week_days)

    return render(request, 'student_timetable.html', {
        'month_days': month_days,
        'empty_days_range': empty_days_range,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    })