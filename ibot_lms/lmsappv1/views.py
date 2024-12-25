from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Avg
# from .filters import CourseFilter
from .models import User, OfflinePurchase, Module, Course, Assessment, Certification, CertificationQuestion, Category, Product
from .serializers import CourseSerializer, CertificationQuestionSerializer, CourseUserSerializer, CertificationSerializer, ProductImgSerializer, UserSerializer, CourseImgSerializer, ModuleSerializer, OfflinePurchaseSerializer, AssessmentSerializer, CategorySerializer, ProductSerializer, ProductCategorySerializer
from .methods import generate_otp, purchasedUser_encode_token,visitor_encode_token,courseSubscribedUser_encode_token, admin_encode_token, encrypt_password
from .authentication import PurchasedUserTokenAuthentication, CourseSubscribedUserTokenAuthentication, AdminTokenAuthentication, VisitorTokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from cloudinary.uploader import upload
import cloudinary.uploader
from django.core.files.storage import default_storage  # To save files locally
import os
import logging
import razorpay
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from rest_framework import generics
from .tasks import add
from celery.result import AsyncResult

logger = logging.getLogger(__name__)
UPLOAD_DIR = '/media/'
client = razorpay.Client(auth=("rzp_test_88QnZEgha1Ucxs", "yMHU4vBu66sKyux6DJ7OfKu8"))

class SignInAPIView(APIView):
    def post(self, request):
        try:
            print(request.data)
            data = request.data
            email = data.get("email")
            password = data.get("password")
            logger.info(f"Request: {request.method} {request.get_full_path()}")
            user = User.objects.get(email=email)
            logger.info(user)
            encryptPassword = encrypt_password(password) 
            print(user.role)
            if user.subscription:
                if user.role == 'visitor':
                    user.role = 'purchasedUser'
                    user.save()
            if user.password == encryptPassword:
                if user.role == "purchasedUser":
                    token = purchasedUser_encode_token({"id": str(user.id), "role": user.role})
                elif user.role == "CourseSubscribedUser":
                    token = courseSubscribedUser_encode_token({"id": str(user.id), "role": user.role})
                elif user.role == "admin":
                    token = admin_encode_token({"id": str(user.id), "role": user.role})
                elif user.role == "visitor":
                    token = visitor_encode_token({"id": str(user.id), "role": user.role})
                else:
                    return Response(
                        {"message": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST
                    )
                
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "token": str(token),
                        "access": str(refresh.access_token),
                        "data": {"user_id":user.id,'username':user.username, "subscription":user.subscription, "role": user.role},  
                        "message": "User logged in successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            logger.info("User not found")
            logger.error("User not found")
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(e)
            return Response({"message": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
    
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

class SignUpAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        email = data.get('email')
        mobile = data.get('mobile')
        
        if OfflinePurchase.objects.filter(customer_email=email).exists() or OfflinePurchase.objects.filter(customer_contact_number=mobile).exists():
            data['subscription'] = True
        else:
            data['subscription'] = False

        serializer = UserSerializer(data=data)
        
        if serializer.is_valid():
            raw_password = serializer.validated_data.get('password')
            encrypted_password = encrypt_password(raw_password)
            serializer.save(password=encrypted_password)
            logger.info(serializer.data)
            return Response({'data': serializer.data, 'message': "User created successfully"}, status=status.HTTP_201_CREATED)
        else:
            logger.error(serializer.errors)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        data = request.data
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user, data=data)
        
        if serializer.is_valid():
            raw_password = serializer.validated_data.get('password')
            encrypted_password = encrypt_password(raw_password)
            serializer.save(password=encrypted_password)
            return Response({'data': serializer.data, 'message': "User updated successfully"})
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, *args, **kwargs):
        data = request.data
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user, data=data, partial=True)  # Partial update
            if serializer.is_valid():
                raw_password = serializer.validated_data.get('password')
                if raw_password:
                    encrypted_password = encrypt_password(raw_password)
                    serializer.save(password=encrypted_password)
                else:
                    serializer.save()
                return Response({'data': serializer.data, 'message': "User updated successfully"})
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class CourseListCreateAPIView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        logger.info(f"Request: {request.method} {request.get_full_path()}")
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        logger.error(f"Error: {serializer.errors}")
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CourseDetailAPIView(APIView):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, context={'request': request})
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        course.delete()
        return Response({'message': 'Course deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class ModuleAPIView(APIView):
    # Create a new module
    def post(self, request, *args, **kwargs):
        # Extract files and data
        print(request.data)
        intro_file = request.FILES.get('intro')
        content_file = request.FILES.get('content')
        activity_file = request.FILES.get('activity')

        # Include files in request data
        data = request.data.dict()  # Convert QueryDict to standard dict
        data['intro'] = intro_file
        data['content'] = content_file
        data['activity'] = activity_file

        # Serialize and save
        serializer = ModuleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get all modules for a specific course
    def get(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        if course_id:
            modules = Module.objects.filter(course_id=course_id)
            serializer = ModuleSerializer(modules, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Update a module by module ID
    def put(self, request, *args, **kwargs):
        module_id = kwargs.get('module_id')
        module = get_object_or_404(Module, id=module_id)
        serializer = ModuleSerializer(module, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # Delete a module by module ID
    def delete(self, request, *args, **kwargs):
        module_id = kwargs.get('module_id')
        module = get_object_or_404(Module, id=module_id)
        module.delete()
        return Response({'message': 'Module deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
class ModuleFileAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve query parameters
        print(request.query_params)
        module_id = request.query_params.get('module_id')
        file_path = request.query_params.get('file_path')
        
        if not module_id or not file_path:
            return Response(
                {"error": "module_id and file_path are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate module existence
        module = get_object_or_404(Module, id=module_id)
        print(module.intro.name)
        print(module.content.name)
        print(module.activity.name)

        # Verify file_path matches any of the module's file fields
        if file_path in [module.intro.name, module.content.name, module.activity.name]:
            print(module.intro.storage.path(file_path))
            file_full_path = module.intro.storage.path(file_path)
            try:
                # Serve the file
                return FileResponse(open(file_full_path, 'rb'), content_type='application/pdf')
            except FileNotFoundError:
                raise Http404("File not found.")
        else:
            print
            return Response(
                {"message": "The file path does not match any files in this module."},
                status=status.HTTP_400_BAD_REQUEST,
            )

class ModuleDetailAPIView(APIView):
    # GET request to retrieve the module details by module_id
    def get(self, request, module_id, *args, **kwargs):
        module = get_object_or_404(Module, id=module_id)
        serializer = ModuleSerializer(module)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    # PATCH request to update the module partially by module_id
    def patch(self, request, module_id, *args, **kwargs):
        module = get_object_or_404(Module, id=module_id)
        serializer = ModuleSerializer(module, data=request.data, partial=True)  # partial=True allows partial updates

        if serializer.is_valid():
            serializer.save()  # Save the updated module
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class OfflinePurchaseList(APIView):
    def get(self, request):
        purchases = OfflinePurchase.objects.all()
        serializer = OfflinePurchaseSerializer(purchases, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OfflinePurchaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class OfflinePurchaseDetail(APIView):
    """
    Retrieve, update or delete an offline purchase.
    """
    def get_object(self, id):
        try:
            return OfflinePurchase.objects.get(id=id)
        except OfflinePurchase.DoesNotExist:
            return None

    def get(self, request, id):
        purchase = self.get_object(id)
        if purchase:
            serializer = OfflinePurchaseSerializer(purchase)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        purchase = self.get_object(id)
        if purchase:
            serializer = OfflinePurchaseSerializer(purchase, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        purchase = self.get_object(id)
        if purchase:
            purchase.delete()
            return Response({"message": "Offline purchase deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
class AssessmentCreateAPIView(APIView):
    def post(self, request):
        serializer = AssessmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, module_id):
        assessments = Assessment.objects.filter(module_id=module_id)
        serializer = AssessmentSerializer(assessments, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

class AssessmentDetailAPIView(APIView):
    def get(self, request, pk):
        assessment = get_object_or_404(Assessment, id=pk)
        serializer = AssessmentSerializer(assessment)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        assessment = get_object_or_404(Assessment, id=pk)
        serializer = AssessmentSerializer(assessment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        assessment = get_object_or_404(Assessment, id=pk)
        serializer = AssessmentSerializer(assessment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        assessment = get_object_or_404(Assessment, id=pk)
        assessment.delete()
        return Response({"message": "Assessment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class CategoryAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        age = request.query_params.get('age', None)
        level = request.query_params.get('level', None)

        if age:
            categories = categories.filter(age=age)
        if level:
            categories = categories.filter(level=level)
        
        serializer = CategorySerializer(categories, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
class ProductAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                product = Product.objects.get(pk=pk)
                serializer = ProductCategorySerializer(product, context={'request': request})
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            except Product.DoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            products = Product.objects.all()
            serializer = ProductImgSerializer(products, many=True, context={'request': request})
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        serializer = ProductSerializer(data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        logger.error(serializer.errors)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
class CourseUserVisibilityAPIView(APIView):
    def get(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id')
        status_value = request.query_params.get('status')
        if not course_id:
            return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if status_value not in ['true', 'false']:
            return Response({"error": "status must be 'true' or 'false'"}, status=status.HTTP_400_BAD_REQUEST)

        status_bool = status_value.lower() == 'true'
        course = get_object_or_404(Course, id=course_id)
        course.status = status_bool
        course.save()

        return Response({"data": {"course_id": course_id, "status": status_bool}, "message": "Course status updated successfully"}, status=status.HTTP_200_OK)

class CertificationAPIView(APIView):
    def post(self, request):
        course_id = request.data.get("course")
        if Certification.objects.filter(course_id=course_id).exists():
            return Response(
                {"message": "A certification for this course already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CertificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD)
                        
    def get(self, request, *args, **kwargs):
        cert_id = kwargs.get('id', None)
        course_id = request.query_params.get('course_id', None)

        if cert_id:
            certification = get_object_or_404(Certification, id=cert_id)
            serializer = CertificationSerializer(certification)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        if course_id:
            certifications = Certification.objects.filter(course__id=course_id)
            serializer = CertificationSerializer(certifications, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        return Response({"error": "No valid ID or course ID provided."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        certification = get_object_or_404(Certification, id=id)
        serializer = CertificationSerializer(certification, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        certification = get_object_or_404(Certification, id=id)
        certification.delete()
        return Response({"message": "Certification deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class CertificationQuestionAPIView(APIView):
    def post(self, request):
        serializer = CertificationQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        cert_quest_id = kwargs.get('id', None)
        cert_id = request.query_params.get('certification_id', None)

        if cert_id:
            questions = CertificationQuestion.objects.filter(certification__id=cert_id)
            serializer = CertificationQuestionSerializer(questions, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        
        if cert_quest_id:
            question = get_object_or_404(CertificationQuestion, id=cert_quest_id)
            serializer = CertificationQuestionSerializer(question)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        return Response({"message": "Certification ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        question = get_object_or_404(CertificationQuestion, id=id)
        serializer = CertificationQuestionSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        question = get_object_or_404(CertificationQuestion, id=id)
        question.delete()
        return Response({"message": "Certification question deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
