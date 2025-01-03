# Generated by Django 5.1.1 on 2024-12-27 08:26

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lmsappv1', '0009_remove_course_course_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deleteaccount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reason', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(blank=True, max_length=100, null=True, unique=True)),
                ('username', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('mobile', models.CharField(blank=True, max_length=15, null=True)),
                ('password', models.CharField(blank=True, max_length=100, null=True)),
                ('otp', models.TextField(max_length=4)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('rating', models.IntegerField(default=1)),
                ('review', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lmsappv1.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_rating', to='lmsappv1.user')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('razorpay_signature', models.CharField(blank=True, max_length=255, null=True)),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('currency', models.CharField(default='INR', max_length=10)),
                ('status', models.CharField(choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed'), ('PENDING', 'Pending')], default='PENDING', max_length=20)),
                ('receipt', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='lmsappv1.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserAssessmentScore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_marks', models.IntegerField(default=0)),
                ('obtained_marks', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lmsappv1.course')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lmsappv1.module')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_scores', to='lmsappv1.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserCertificationScore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_marks', models.IntegerField(default=0)),
                ('obtained_marks', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('certify', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lmsappv1.certification')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lmsappv1.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certification_score', to='lmsappv1.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserCourseProgress',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.IntegerField(default=0)),
                ('activity', models.IntegerField(default=0)),
                ('task', models.CharField(choices=[('overview', 'overview'), ('main', 'main'), ('activity', 'activity'), ('assessment', 'assessment'), ('certifyques', 'certifyques')], max_length=100)),
                ('is_completed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lmsappv1.course')),
                ('last_module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lmsappv1.module')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_progress', to='lmsappv1.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserReview',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('rating', models.IntegerField(default=1)),
                ('review', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lmsappv1.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_rating', to='lmsappv1.user')),
            ],
        ),
    ]
