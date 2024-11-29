# Generated by Django 5.1.2 on 2024-11-28 17:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0003_remove_user_lesson_preferences'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_due', models.DecimalField(decimal_places=2, max_digits=8)),
                ('due_date', models.DateField()),
                ('payment_status', models.CharField(choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], max_length=20)),
                ('invoice_date', models.DateField(auto_now_add=True)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LessonBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.TextField(max_length=100)),
                ('duration', models.IntegerField()),
                ('time', models.TimeField()),
                ('lesson_date', models.DateField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_lessons', to=settings.AUTH_USER_MODEL)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_lessons', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LessonRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Unallocated', 'Unallocated'), ('Allocated', 'Allocated'), ('Pending', 'Pending'), ('Cancelled', 'Cancelled')], default='Unallocated', max_length=20)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('requested_topic', models.TextField(blank=True, help_text='Describe what you would like to learn (e.g Web Development with Django)')),
                ('requested_frequency', models.TextField(help_text='How often would you like your lessons (e.g Weekly, Fortnightly)?', max_length=20)),
                ('requested_duration', models.IntegerField(help_text='Lesson duration in minutes')),
                ('requested_time', models.TimeField(help_text='Preferred time for the lesson')),
                ('experience_level', models.TextField(help_text='Describe your level of experience with this topic.')),
                ('additional_notes', models.TextField(blank=True, help_text='Additional information or requests')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
