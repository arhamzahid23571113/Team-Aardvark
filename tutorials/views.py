from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.urls import reverse
from calendar import monthrange, SUNDAY
from datetime import date
from calendar import Calendar, monthrange
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from calendar import monthrange
from datetime import datetime, timedelta, date
from django.utils.timezone import make_aware
from django.shortcuts import render
from datetime import timedelta
from .models import User, Invoice
from .models import LessonRequest
from django.shortcuts import get_object_or_404, redirect
from .forms import LessonBookingForm,ContactMessages
from .models import ContactMessage
from .forms import AdminReplyBack
from django.utils.timezone import now
from django.http import HttpResponseForbidden




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


def generate_invoice(invoice, term_start=None, term_end=None):
    total = 0

    if term_start and term_end:
        lesson_requests = LessonRequest.objects.filter(
            student=invoice.student, 
            request_date__range=[term_start, term_end], 
            status='Allocated')
    else:
        lesson_requests = LessonRequest.objects.filter(
            student=invoice.student, 
            status='Allocated')
        
    for booking in lesson_requests:
        booking.lesson_price = (booking.requested_duration / 60) * settings.HOURLY_RATE
        total += booking.lesson_price 

    if total == 0:
        invoice.payment_status = 'Paid' 
    else:
        'Unpaid'

    return lesson_requests, total
        

@login_required
def manage_invoices(request):
    invoices = Invoice.objects.all()
    invoice_data = []

    for invoice in invoices:
        lesson_requests, total = generate_invoice(invoice)
        invoice.standardised_due_date = invoice.due_date.strftime("%d/%m/%Y")

        invoice_data.append({
            'invoice' : invoice,
            'lesson_requests' : lesson_requests,
            'total' : total,
        })

    return render(request, 'manage_invoices.html', {'invoice_data' : invoice_data})

def admin_invoice_view(request, invoice_num):
    invoice = get_object_or_404(Invoice, invoice_num=invoice_num)

    lesson_requests, total = generate_invoice(invoice)

    for booking in lesson_requests:
        booking.standardised_date = booking.request_date.strftime("%d/%m/%Y")

    base_template = 'dashboard_base_admin.html' if request.user.role == 'admin' else 'dashboard_base_student.html'

    return render(request, 'invoice_page.html', {
        'invoice': invoice,
        'lesson_requests': lesson_requests,
        'total': total,
        'is_admin': True,  
        'base_template' : base_template,
    })

@login_required
def invoice_page(request, term_name = None):
    """Display user invoice."""
    terms = {
        'autumn': (date(2024, 9, 1), date(2024, 12, 31)),
        'spring': (date(2025, 1, 1), date (2025, 5, 31)),
        'summer': (date(2025, 6, 1), date(2025, 8, 31)),
    }

    if term_name is None:
        today = date.today()

        for term, (start, end) in terms.items():
            if start <= today <= end:
                term_name = term 
                break 

    term_dates = terms.get(term_name)
    term_start, term_end = term_dates

    invoice = Invoice.objects.filter(student=request.user).first()
    
    term_keys = list(terms.keys())
    current_term_index = term_keys.index(term_name)

    previous_term = term_keys[(current_term_index - 1) % len(term_keys)]
    next_term = term_keys[(current_term_index + 1) % len(term_keys)]

    lesson_requests, total = generate_invoice(invoice, term_start, term_end)

    for booking in lesson_requests:
        booking.standardised_date = booking.request_date.strftime("%d/%m/%Y")

    base_template = 'dashboard_base_admin.html' if request.user.role == 'admin' else 'dashboard_base_student.html'

    return render(request, 'invoice_page.html', {
        'invoice': invoice, 
        'lesson_requests': lesson_requests,
        'total': total, 
        'term_name': term_name.title(),
        'previous_term': previous_term,
        'next_term': next_term,
        'base_template' : base_template,
        })


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
        return reverse('log_in')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen and handle profile modifications."""

    model = User
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profile updated successfully!")
        return response

    def get_success_url(self):
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

    



from django.shortcuts import redirect, render
from datetime import date
from calendar import monthrange, SUNDAY




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


def see_my_student_timetable(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('log_in')

    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    allocated_lessons = LessonRequest.objects.filter(
        student=request.user,
        tutor__isnull=False,
        status='Allocated'
    ).values(
        'requested_time',
        'requested_date',
        'requested_duration',
        'tutor__first_name',
        'tutor__last_name',
        'requested_topic'
    )

    num_days = monthrange(year, month)[1]
    first_day_of_month = date(year, month, 1)
    start_day = first_day_of_month.weekday()  
    days = []
    week = []
    lessons_by_day = {}

    for lesson in allocated_lessons:
        lesson_date = lesson['requested_date']
        if lesson_date not in lessons_by_day:
            lessons_by_day[lesson_date] = []
        lessons_by_day[lesson_date].append({
            'notes': lesson['requested_topic'],
            'start_time': lesson['requested_time'],
            'end_time': (datetime.combine(date.today(), lesson['requested_time']) + timedelta(
                minutes=lesson['requested_duration']
            )).time(),
            'tutor': f"{lesson['tutor__first_name']} {lesson['tutor__last_name']}"
        })

    current_date = first_day_of_month
    for _ in range(start_day):
        week.append({'date': None})  

    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        day_data = {'date': current_date, 'lessons': lessons_by_day.get(current_date, [])}
        week.append(day_data)
        if len(week) == 7:
            days.append(week)
            week = []
    if week:  
        days.append(week)

    prev_month = month - 1 or 12
    prev_year = year - 1 if prev_month == 12 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if next_month == 1 else year

    context = {
        'month_name': first_day_of_month.strftime('%B'),
        'year': year,
        'month_days': days,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'student_timetable.html', context)



def generate_lessons(lesson_request, num_lessons=10):
    """
    Generate individual lessons from a lesson request.
    - lesson_request: The LessonRequest instance.
    - num_lessons: Number of lessons to generate (default 10).
    """
    start_date = lesson_request.requested_date
    frequency = 7 if lesson_request.requested_frequency == "weekly" else 14
    duration = lesson_request.requested_duration
    
    lessons = []
    for i in range(num_lessons):  # Generate the specified number of lessons
        lesson_date = start_date + timedelta(days=frequency * i)
        lesson = Lesson.objects.create(
            tutor=lesson_request.tutor,
            student=lesson_request.student,
            date=lesson_date,
            time=lesson_request.requested_time,
            duration=duration,
            topic=lesson_request.requested_topic
        )
        lessons.append(lesson)
    return lessons


def see_my_tutor_timetable(request):
    if not request.user.is_authenticated or request.user.role != 'tutor':
        return redirect('log_in')

    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    allocated_lessons = LessonRequest.objects.filter(
        tutor=request.user,
        status='Allocated'
    ).values(
        'requested_time',
        'requested_date',
        'requested_duration',
        'student__first_name',
        'student__last_name',
        'requested_topic'
    )

    lessons_by_day = {}
    for lesson in allocated_lessons:
        lesson_date = lesson['requested_date']
        if lesson_date not in lessons_by_day:
            lessons_by_day[lesson_date] = []
        lessons_by_day[lesson_date].append({
            'notes': lesson['requested_topic'],
            'start_time': lesson['requested_time'],
            'end_time': (datetime.combine(date.today(), lesson['requested_time']) + timedelta(
                minutes=lesson['requested_duration']
            )).time(),
            'student': f"{lesson['student__first_name']} {lesson['student__last_name']}"
        })

    num_days = monthrange(year, month)[1]
    first_day_of_month = date(year, month, 1)
    start_day = first_day_of_month.weekday()
    days = []
    week = []

    for _ in range(start_day):
        week.append({'date': None})

    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        day_data = {'date': current_date, 'lessons': lessons_by_day.get(current_date, [])}
        week.append(day_data)
        if len(week) == 7:
            days.append(week)
            week = []
    if week:
        days.append(week)

    prev_month = month - 1 or 12
    prev_year = year - 1 if prev_month == 12 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if next_month == 1 else year

    context = {
        'month_name': first_day_of_month.strftime('%B'),
        'year': year,
        'month_days': days,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    return render(request, 'tutor_timetable.html', context)
    

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
        return redirect('log_in')

@login_required
def view_tutor_messages(request,role=None):
    if request.user.role == 'admin':
        tutor_messages = ContactMessage.objects.filter(role='tutor').order_by('timestamp')
        return render(request,'admin_messages_tutors.html',{'messages':tutor_messages})
    else:
        return redirect('log_in')


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




from django.shortcuts import redirect, render
from datetime import date
from calendar import monthrange, SUNDAY

def timetable_view(request):
    today = date.today()
    selected_month = int(request.GET.get('month', today.month))  # Default to current month
    selected_year = int(request.GET.get('year', today.year))  # Default to current year

    # Ensure user is authenticated
    if not request.user.is_authenticated:
        return redirect('log_in')

    user = request.user

    # Get calendar for the selected month and year
    cal = Calendar(SUNDAY)
    month_days = cal.monthdayscalendar(selected_year, selected_month)

    # Prepare lessons for each day
    structured_month_days = []
    for week in month_days:
        week_data = []
        for day in week:
            if day == 0:  # Empty day for alignment
                week_data.append({'date': None, 'lessons': None})
            else:
                day_date = date(selected_year, selected_month, day)
                lessons = []
                if user.role == 'student':
                    lessons = Lesson.objects.filter(student=user, date=day_date)
                elif user.role == 'tutor':
                    lessons = Lesson.objects.filter(tutor=user, date=day_date).order_by('start_time')
                week_data.append({'date': day_date, 'lessons': lessons})
        structured_month_days.append(week_data)

    # Calculate previous and next months
    prev_month = selected_month - 1 if selected_month > 1 else 12
    prev_year = selected_year - 1 if prev_month == 12 else selected_year
    next_month = selected_month + 1 if selected_month < 12 else 1
    next_year = selected_year + 1 if next_month == 1 else selected_year

    context = {
        'month_days': structured_month_days,
        'year': selected_year,
        'month': selected_month,
        'month_name': date(selected_year, selected_month, 1).strftime('%B'),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    return render(request, 'student_timetable.html', context)


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
    # Ensure only students can access this page
    if request.user.role != 'student':
        return redirect('log_in')
    
    assigned_tutors = LessonRequest.objects.filter(
        student=request.user,  
        tutor__isnull=False,   
        status='Allocated'     # Optional: Only show allocated tutors
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
    if request.user.role != 'admin':  # Only admins can access this page
        return redirect('log_in')  # Redirect unauthorized users to login
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
        # Fetch the lesson request and selected tutor 
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
        tutor_id = request.POST.get('tutor_id')

        if tutor_id:
            tutor = get_object_or_404(User, id=tutor_id, role='tutor')
            # Assign the tutor to the lesson request (assuming you have a 'tutor' field)
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
         return render(request, 'admin_reply.html', {'form': adminForm, 'message': message})

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


@login_required
def tutor_profile(request):
    """Display the tutor's profile."""
    if request.user.role != 'tutor':
        messages.error(request, "Access denied. Only tutors can view this page.")
        return redirect('dashboard')

    tutor = request.user

    context = {
        'tutor': tutor,
    }
    return render(request, 'tutor_profile.html', context)


@login_required
def edit_profile(request):
    """Allow the tutor to edit their profile details, including profile picture and expertise."""
    user = request.user

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user, user=user)
        if form.is_valid():
            # Save profile changes, including expertise and profile picture
            user = form.save(commit=False)
            user.expertise = form.cleaned_data.get('expertise')  # Ensure expertise is saved
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('tutor_profile')
    else:
        form = UserForm(instance=user, user=user)

    # Determine the base template based on the user's role
    profile_base_template = 'dashboard_base_tutor.html' if user.role == 'tutor' else 'dashboard.html'

    return render(request, 'edit_my_tutor_profile.html', {
        'form': form,
        'profile_base_template': profile_base_template,
    })
