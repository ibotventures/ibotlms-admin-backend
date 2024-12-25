from django.db import models
from django.utils import timezone
import uuid

class User(models.Model):
    Role = (
        ('purchasedUser', 'purchasedUser'),
        ('CourseSubscribedUser', 'CourseSubscribedUser'),
        ('admin', 'admin'),
        ('visitor', 'visitor'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    password = models.CharField(max_length=100)
    age = models.CharField(max_length=3, null=True, blank=True)
    profile = models.TextField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=50, choices=Role, default='visitor')
    subscription = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_age = models.PositiveIntegerField(help_text="Recommended age for the category")
    end_age = models.PositiveIntegerField(help_text="Recommended age for the category")
    level = models.CharField(max_length=50, help_text="Skill or experience level for the category")
    category_name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    product_image = models.ImageField(upload_to='product/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    make = models.CharField(max_length=255, help_text="Manufacturer or brand of the product")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_name = models.CharField(max_length=255)
    course_description = models.TextField(null=True, blank=True)
    course_duration = models.IntegerField(help_text="Duration in hours")
    status = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='courses')
    course_cover_image = models.ImageField(upload_to='course/', null=True, blank=True)
    video = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module_name = models.CharField(max_length=255)
    module_description = models.TextField(null=True, blank=True)
    intro = models.FileField(upload_to='intro/', null=True, blank=True)
    content = models.FileField(upload_to='content/', null=True, blank=True)
    activity = models.FileField(upload_to='activity/', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assessments')
    question = models.TextField(null=True, blank=True)
    option1 = models.TextField(null=True, blank=True)
    option2 = models.TextField(null=True, blank=True)
    option3 = models.TextField(null=True, blank=True)
    option4 = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class Certification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, related_name='certifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class CertificationQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certification = models.ForeignKey(Certification, related_name='questions', on_delete=models.CASCADE)
    question = models.TextField(null=True, blank=True)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class OfflinePurchase(models.Model):
    Payment_Types = (
        ('online', 'online'),
        ('offline', 'offline'),
        ('cheque', 'cheque'),
        ('neft', 'neft'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor_name = models.CharField(max_length=100)
    vendor_contact_name = models.CharField(max_length=100)
    vendor_contact_number = models.CharField(max_length=15)
    vendor_email = models.EmailField(max_length=100)
    vendor_address = models.TextField()
    customer_name = models.CharField(max_length=100)
    customer_contact_name = models.CharField(max_length=100)
    customer_contact_number = models.CharField(max_length=15)
    customer_email = models.EmailField(max_length=100)
    customer_address = models.TextField()
    payment_term = models.CharField(max_length=100, choices=Payment_Types, default='offline')
    order_id = models.CharField(max_length=100)
    transaction_number = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offline_purchases')
    product_quantity = models.IntegerField()
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
