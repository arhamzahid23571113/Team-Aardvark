from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
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
from django.shortcuts import render
from datetime import timedelta
from tutorials.models import User

from tutorials.models import LessonRequest
from django.shortcuts import get_object_or_404, redirect
from tutorials.forms import LessonBookingForm
from tutorials.models import ContactMessage


@login_required
def student_dashboard(request):
    """Student-specific dashboard."""
    return render(request, 'student_dashboard.html')

@login_required
def request_lesson(request):
    """
    Handles lesson requests by students, ensuring no double-booking occurs.
    """
    if request.method == 'POST':
        form = LessonBookingForm(request.POST)
        if form.is_valid():
            lesson_request = form.save(commit=False)  
            lesson_request.student = request.user  

            try:

                lesson_request.full_clean()
                lesson_request.save()
                messages.success(request, "Your lesson request has been successfully submitted!")
                return redirect('lesson_request_success')
            except ValidationError as e:

                for field, error_list in e.message_dict.items():
                    for error in error_list:
                        form.add_error(field, error)
                messages.error(request, "There was an error with your submission. Please check below.")

                logger.error("Lesson request validation failed: %s", e.message_dict)

    else:
        form = LessonBookingForm()

    return render(request, 'request_lesson.html', {'form': form})

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

@login_required
def student_messages(request):
    student = request.user
    studentMessages = ContactMessage.objects.filter(user=student).order_by('timestamp')
    return render(request,'student_messages.html',{'messages':studentMessages})    

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

@login_required
def student_profile(request):
    """Display the student's profile."""
    if request.user.role != 'student':
        messages.error(request, "Access denied. Only students can view this page.")
        return redirect('dashboard')

    student = request.user

    context = {
        'student': student,
    }
    return render(request, 'student_profile.html', context)