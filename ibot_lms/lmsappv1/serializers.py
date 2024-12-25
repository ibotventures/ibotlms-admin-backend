from rest_framework import serializers
from .models import User, OfflinePurchase, Course, Module, Assessment, Certification, CertificationQuestion, Category, Product
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        
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
        
class CertificationQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationQuestion
        fields = '__all__'