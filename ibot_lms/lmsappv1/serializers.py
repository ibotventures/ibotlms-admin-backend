from rest_framework import serializers
from .models import CartData, SubscriptionMoney, User, OfflinePurchase, Course, Module, Assessment, Certification, CertificationQuestion, Category, Product, UserCourseProgress, UserAssessmentScore, UserCertificationScore, ProductReview, UserReview, Deleteaccount, OTP, Transaction, UserCourseProgress, ProductReview, UserReview
from django.core.files.storage import default_storage

from rest_framework import serializers
from django.core.files.storage import default_storage

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_name', 'course_description', 'course_duration', 'status', 'product', 'course_cover_image', 'video']
        
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
class CourseFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        
class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','password','email','mobile','subscription']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'

class OfflinePurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfflinePurchase
        fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'description', 'category', 'price', 'make', 'product_image']

    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product_image:
            return request.build_absolute_uri(obj.product_image.url)
        return None

class CourseImgSerializer(serializers.ModelSerializer):
    course_cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_course_cover_image(self, obj):
        request = self.context.get('request')
        if obj.course_cover_image:
            return request.build_absolute_uri(obj.course_cover_image.url)
        return None

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'role', 'subscription']

    def update(self, instance, validated_data):
        new_image = validated_data.get('profile')
        if new_image and instance.profile:
            old_image_path = instance.profile.path
            if default_storage.exists(old_image_path):
                default_storage.delete(old_image_path)

        return super().update(instance, validated_data)

class CertificationQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationQuestion
        fields = ['question', 'option1', 'option2', 'option3', 'option4', 'answer', 'id']

class CertificationsSerializer(serializers.ModelSerializer):
    questions = CertificationQuestionSerializer(many=True)

    class Meta:
        model = Certification
        fields = ['name', 'description', 'duration', 'questions', 'course']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        certification = Certification.objects.create(**validated_data)
        for question_data in questions_data:
            CertificationQuestion.objects.create(certification=certification, **question_data)
        return certification

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions')
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.save()

        for question_data in questions_data:
            question_id = question_data.get('id')
            if question_id:
                question = CertificationQuestion.objects.get(id=question_id, certification=instance)
                for field, value in question_data.items():
                    setattr(question, field, value)
                question.save()
            else:
                CertificationQuestion.objects.create(certification=instance, **question_data)

        return instance

class UserCourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourseProgress
        fields = ['id', 'user', 'course', 'course_name', 'last_module', 'last_module_name', 'last_task', 'last_task_name', 'is_completed', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class StatisticsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    purchased_users = serializers.IntegerField()
    subscribed_users = serializers.IntegerField()
    users_by_role = serializers.DictField(child=serializers.IntegerField())

    total_purchases = serializers.IntegerField()
    purchases_by_product = serializers.DictField(child=serializers.IntegerField())
    revenue_by_product = serializers.DictField(child=serializers.FloatField())
    purchases_by_payment_method = serializers.DictField(child=serializers.IntegerField())

    total_courses = serializers.IntegerField()
    courses_by_level = serializers.DictField(child=serializers.IntegerField())
    courses_by_age_category = serializers.DictField(child=serializers.IntegerField())
    courses_by_product = serializers.DictField(child=serializers.IntegerField())

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = '__all__'

class TransactionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user_id', 'amount', 'currency', 'receipt']

class TransactionCheckOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user_id', 'razorpay_payment_id', 'razorpay_order_id', 'razorpay_signature']

class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_name', 'course_description', 'course_duration', 'age_category', 'level']

class CourseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_name', 'course_description', 'course_duration', 'age_category', 'level']


class CourseImgSerializer(serializers.ModelSerializer):
    course_cover_image = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = '__all__'
    def get_course_cover_image(self, obj):
        request = self.context.get('request')
        if obj.course_cover_image:
            return request.build_absolute_uri(obj.course_cover_image.url)
        return 
    
class ProductImgSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'
    def get_product_image(self, obj):
        request = self.context.get('request')
        if request and obj.product_image:
            return request.build_absolute_uri(obj.product_image.url)
        return None
    
class CourseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['status']
        
class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'
        
class UserdetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password','role','subscription']  

    def update(self, instance, validated_data):
        new_image = validated_data.get('profile')
        if new_image and instance.profile:
            old_image_path = instance.profile.path
            if default_storage.exists(old_image_path):
                default_storage.delete(old_image_path)

        # Update instance with validated data
        return super().update(instance, validated_data)
    
class TasktrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourseProgress
        fields='__all__'
        
class UserAssessmentSerialiser(serializers.ModelSerializer):
    class Meta:
        model= UserAssessmentScore
        fields = '__all__'
class UserCertificationSerialiser(serializers.ModelSerializer):
    class Meta:
        model= UserCertificationScore
        fields = '__all__'
class UserReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReview
        fields = '__all__'
class delserialiser(serializers.ModelSerializer):
    class Meta:
        model = Deleteaccount
        fields = '__all__'
class Productreviewserialiser(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'
        
class categoryserialiser(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']

class subscribeserialiser(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionMoney
        fields = ['id','amount','receiptcount']

class transactiondetails(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id','user_id','razorpay_order_id','razorpay_payment_id','amount','receipt']

class cartserialiser(serializers.ModelSerializer):
    class Meta:
        model = CartData
        fields = ['user','product','amount']

class cartserial(serializers.ModelSerializer):
        class Meta:
            model = CartData
            fields = ['id','quantity','user','product','amount']