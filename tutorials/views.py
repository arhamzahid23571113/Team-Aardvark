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
from .models import User,LessonBooking
from .models import LessonRequest
from django.shortcuts import get_object_or_404, redirect
from .forms import LessonBookingForm,ContactMessages
from .models import ContactMessage
from .forms import AdminReplyBack
from django.utils.timezone import now





from .models import Lesson
#AMINA
from django.shortcuts import render
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

     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Determine the base template based on the user's role
        if hasattr(self.request.user, 'role'):  # Ensure the role attribute exists
            if self.request.user.role == 'tutor':
                profile_base_template = 'dashboard_base_tutor.html'
            elif self.request.user.role == 'student':
                profile_base_template = 'dashboard_base_student.html'
            elif self.request.user.role == 'admin':
                profile_base_template = 'dashboard_base_admin.html'
            else:
                profile_base_template = 'dashboard.html'  # Default for other roles
        else:
            profile_base_template = 'dashboard.html'

        context['profile_base_template'] = profile_base_template
        return context


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
        return reverse('log_in')

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


#STUDENTS
@login_required
def request_lesson(request):
    if request.method == 'POST':
        form = LessonBookingForm(request.POST)
        if form.is_valid():
            lesson_request = form.save(commit=False)
            lesson_request.student = request.user  
            lesson_request.save()
            return redirect('lesson_request_success')  
        else:
            
            print(form.errors)
    else:
        form = LessonBookingForm()

    return render(request, 'request_lesson.html', {'form': form})

#STUDENT OR TUTOR
@login_required
def contact_admin(request):
    if request.user.is_authenticated:
        if request.user.role == 'tutor':
            base_template = 'dashboard_base_tutor.html'
        elif request.user.role == 'student':
            base_template = 'dashboard_base_student.html'
        elif request.user.role == 'admin':
            base_template = 'dashboard_base_admin.html'
        else:
            base_template = 'dashboard.html'  
    else:
        base_template = 'dashboard.html'  
    return render(request, 'contact_admin.html', {'base_template': base_template})


#STUDENTS
@login_required
def see_my_tutor(request):
    if request.user.role != 'student':
        return redirect('log_in')
    
    assigned_tutors = LessonRequest.objects.filter(
        student=request.user,  
        tutor__isnull=False,   
        status='Allocated'     
    ).values(
        'tutor__id',
        'tutor__first_name',
        'tutor__last_name',
        'tutor__email',
        'tutor__expertise'
    ).distinct()

    context = {
        'tutors': assigned_tutors,  
    }
    return render(request, 'my_tutor_profile.html', context)

#TUTORS
@login_required
def see_my_students_profile(request):
    if request.user.role != 'tutor':
        return redirect('log_in')
    assigned_students = (
        User.objects.filter(
            lesson_requests__tutor=request.user  
        )
        .distinct()
    )
    context = {
        'students': assigned_students,
    }
    return render(request, 'my_students_profile.html', context)


#STUDENTS
@login_required
def lesson_request_success(request):
    dashboard_url = reverse('log_in')
    if request.user.is_authenticated:
        if request.user.role == 'tutor':
            base_template = 'dashboard_base_tutor.html'
            dashboard_url = reverse('tutor_dashboard')
        elif request.user.role == 'student':
            base_template = 'dashboard_base_student.html'
            dashboard_url = reverse('student_dashboard')
        elif request.user.role == 'admin':
            base_template = 'dashboard_base_admin.html'
            dashboard_url = reverse('admin_dashboard')
        else:
            base_template = 'dashboard.html'
    else:
        base_template = 'dashboard.html'
    return render(request, 'lesson_request_success.html',{'base_template':base_template,'dashboard_url':dashboard_url})


#ADMINS
@login_required
def student_requests(request):
    lesson_requests = LessonRequest.objects.select_related('student').order_by('student')
    students_with_requests = {}
    for req in lesson_requests:
        if req.student not in students_with_requests:
            students_with_requests[req.student] = []
        students_with_requests[req.student].append(req)

    tutors = User.objects.filter(role='tutor')  

    context = {
        'students_with_requests': students_with_requests,
        'tutors': tutors,
    }
    return render(request, 'student_requests.html', context)



#ADMINS
@login_required
def assign_tutor(request, lesson_request_id):
    if request.method == 'POST':
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
        tutor_id = request.POST.get('tutor_id')

        if tutor_id:
            tutor = get_object_or_404(User, id=tutor_id, role='tutor')
            lesson_request.tutor = tutor
            lesson_request.status = 'Allocated'
            lesson_request.save()

        return redirect('student_requests')  
    

#ADMINS
@login_required
def unassign_tutor(request, lesson_request_id):
    if request.method == 'POST':
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
        lesson_request.tutor = None
        lesson_request.status = 'Unallocated'
        lesson_request.save()
        return redirect('student_requests')
    

#ADMINS
@login_required
def cancel_request(request, lesson_request_id):
    if request.method == 'POST':
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
        lesson_request.status = 'Cancelled'
        lesson_request.tutor = None  
        lesson_request.save()
        return redirect('student_requests')


#ADMINS
@login_required
def all_tutor_profiles(request):
    tutors = User.objects.filter(role='tutor')
    context = {'tutors': tutors}
    return render(request, 'all_tutor_profiles.html', context)

#ADMINS
@login_required
def all_student_profiles(request):
    students = User.objects.filter(role='student')
    context = {'students': students}
    return render(request, 'all_student_profiles.html', context)


#ADMINS
@login_required
def view_tutor_profile(request, tutor_id):
    tutor = get_object_or_404(User, id=tutor_id, role='tutor')
    return render(request, 'view_tutor_profile.html', {'tutor': tutor})


#ADMINS
@login_required
def edit_tutor_profile(request, tutor_id):
    tutor = get_object_or_404(User, id=tutor_id, role='tutor')
    if request.method == 'POST':
        tutor.expertise = request.POST.get('expertise', tutor.expertise)
        tutor.save()
        return redirect('all_tutor_profiles')
    return render(request, 'edit_tutor_profile.html', {'tutor': tutor})

@login_required
def view_student_profile(request, student_id):
    student = get_object_or_404(User, id=student_id, role='student')
    return render(request, 'view_student_profile.html',{'student': student})
    

  #STUDENTS
@login_required
def tutor_more_info(request, tutor_id):
    if request.user.role != 'student':
        return redirect('log_in')
    tutor = get_object_or_404(User, id=tutor_id, role='tutor')
    lessons = LessonRequest.objects.filter(student=request.user, tutor=tutor)
    context = {
        'tutor': tutor,
        'lessons': lessons,
    }
    return render(request, 'tutor_more_info.html', context)

  #ADMIN
@login_required
def admin_messages(request,role=None):
    role = role or request.GET.get('role')
    if role == "all":
        messages = ContactMessage.objects.all().order_by('-timestamp')
    elif role in ['student','tutor']:
        messages = ContactMessage.objects.filter(role=role).order_by('-timestamp')
    else:
        messages = []
    return render(request, 'admin_messages.html', {'messages': messages, 'role_filter': role})


@login_required
def send_message_to_admin(request):
    if request.user.is_authenticated:
        if request.user.role == 'tutor':
            base_template = 'dashboard_base_tutor.html'
        elif request.user.role == 'student':
            base_template = 'dashboard_base_student.html'
        elif request.user.role == 'admin':
            base_template = 'dashboard_base_admin.html'
        else:
            base_template = 'dashboard.html'
    else:
        base_template = 'dashboard.html'

    if request.method == 'POST':
        form = ContactMessages(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.user = request.user  
            contact_message.save()
            messages.success(request, 'Your message has been submitted successfully!')
            return redirect('response_success')
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
        form = ContactMessages()

    return render(request, 'contact_admin.html', {'form': form, 'base_template': base_template})

@login_required
def view_student_messages(request,role=None):
    if request.user.role == 'admin':
        student_messages = ContactMessage.objects.filter(role='student').order_by('timestamp')
        return render(request,'admin_messages_students.html',{'messages':student_messages})
    else:
        return redirect('admin_dashboard')

@login_required
def view_tutor_messages(request,role=None):
    if request.user.role == 'admin':
        tutor_messages = ContactMessage.objects.filter(role='tutor').order_by('timestamp')
        return render(request,'admin_messages_tutors.html',{'messages':tutor_messages})

@login_required
def admin_reply(request, message_id):
    if request.user.role != 'admin':  
        return redirect('log_in')

    message = get_object_or_404(ContactMessage, id=message_id)

    if request.method == 'POST':
        adminForm = AdminReplyBack(request.POST, instance=message)
        if adminForm.is_valid():
            reply_message = adminForm.save(commit=False)
            reply_message.reply_timestamp = now()  
            reply_message.save()
            messages.success(request, f"Reply successfully sent to {message.user.first_name}!")
            return redirect('response_success')
        else:
            messages.error(request, "There was an error with your reply, it has not been saved successfully.")
    else:
        adminForm = AdminReplyBack(instance=message)

    return render(request, 'admin_reply.html', {'form': adminForm, 'message': message})


#ADMINS
@login_required
def response_submitted_success(request):
    dashboard_url = reverse('log_in')
    if request.user.is_authenticated:
        if request.user.role == 'tutor':
            base_template = 'dashboard_base_tutor.html'
            dashboard_url = reverse('tutor_dashboard')
        elif request.user.role == 'student':
            base_template = 'dashboard_base_student.html'
            dashboard_url = reverse('student_dashboard')
        elif request.user.role == 'admin':
            base_template = 'dashboard_base_admin.html'
            dashboard_url = reverse('admin_dashboard')
        else:
            base_template = 'home.html'
    else:
        base_template = 'home.html'
    return render(request, 'response_submitted.html',{'base_template':base_template,'dashboard_url':dashboard_url})

#TUTORS
@login_required
def tutor_messages(request):
    tutor = request.user
    tutorMessages = ContactMessage.objects.filter(user=tutor).order_by('timestamp')
    return render(request,'tutor_messages.html',{'messages':tutorMessages})

@login_required
def student_messages(request):
    student = request.user
    studentMessages = ContactMessage.objects.filter(user=student).order_by('timestamp')
    return render(request,'student_messages.html',{'messages':studentMessages})    
#AMINA    
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