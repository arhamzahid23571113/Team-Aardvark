from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from calendar import monthrange
from datetime import date
from calendar import monthrange
from django.shortcuts import render
from calendar import monthrange
from datetime import datetime, timedelta, date
from django.shortcuts import render
from datetime import timedelta
from tutorials.models import User, LessonRequest, ContactMessage, Lesson
from django.shortcuts import redirect

@login_required
def tutor_dashboard(request):
    """Tutor-specific dashboard."""
    return render(request, 'tutor_dashboard.html')


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
    for i in range(num_lessons):  
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

@login_required
def tutor_messages(request):
    tutor = request.user
    tutorMessages = ContactMessage.objects.filter(user=tutor).order_by('timestamp')
    return render(request,'tutor_messages.html',{'messages':tutorMessages})

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