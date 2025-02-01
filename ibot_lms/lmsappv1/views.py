from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Avg
from .filters import CourseFilter,ProductFilter
from .models import CartData, SubscriptionMoney, User, OfflinePurchase, Module, Course, Assessment, Certification, CertificationQuestion, Category, Product, UserCourseProgress, UserAssessmentScore, UserCertificationScore, ProductReview, UserReview, Deleteaccount, OTP, Transaction, UserCourseProgress, ProductReview, UserReview,AdvertisementBanner, ActivityFile
from .serializers import (
    CourseCreateSerializer,
    CourseFilterSerializer,
    CourseSerializer,
    CertificationQuestionSerializer,
    SignUpSerializer,
    UserAssessmentSerialiser,
    CourseUserSerializer,
    CertificationSerializer,
    ProductImgSerializer,
    UserSerializer,
    CourseImgSerializer,
    ModuleSerializer,
    OfflinePurchaseSerializer,
    AssessmentSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductCategorySerializer,
    UserdetailsSerializer,
    OTPSerializer,
    UserCourseProgressSerializer,
    TasktrackSerializer,
    UserReviewSerializer,
    delserialiser,
    Productreviewserialiser,
    UserCourseProgressSerializer,
    UserReviewSerializer,
    cartserialiser,
    cartserial,
    TransactionCheckOutSerializer,
    TransactionOrderSerializer,
    subscribeserialiser, 
    transactiondetails,
    UserCertificationSerialiser,
    CertificationsSerializer,
    Adserial,
    ActivitiesSerializers

)
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
from django.utils import timezone



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
    
    def patch(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        user = User.objects.get(pk=pk)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

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
        serializer = SignUpSerializer(data=data)
        if serializer.is_valid():
            raw_password = serializer.validated_data.get('password')
            encrypted_password = encrypt_password(raw_password)
            serializer.save(password=encrypted_password)
            return Response({'data': serializer.data, 'message': "User created successfully"}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
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
        serializer = CourseCreateSerializer(data=request.data)
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


def delete_existing_file(file_field):
    """
    Helper function to delete an existing file.
    Deletes from Cloudinary if the file is PowerPoint; from local storage if PDF.
    """
    if file_field:
        if file_field.name.endswith(('.ppt', '.pptx')):
            # Delete from Cloudinary
            file_url = file_field.url
            public_id = file_url.split('/')[-1]
            print(f"Deleting Cloudinary file with public_id: {public_id}")
            result = cloudinary.uploader.destroy(public_id, resource_type="raw")
            print(f"Cloudinary deletion result: {result}")
        elif file_field.name.endswith('.pdf'):
            # Delete from local storage
            if default_storage.exists(file_field.name):
                default_storage.delete(file_field.name)

class Userscheck(APIView):
    def get(self,request):
        try:
            authorize = AdminTokenAuthentication()
            user, role = authorize.authenticate(request)
            if user and role == 'admin':
                response_data = {'data': 'allowed'}
            else:
                response_data = {'data': 'unallow'}
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Signup(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            code = request.data.get('code')
            forget = request.data.get('forget')
            otp = OTP.objects.filter(email=email,otp=code).first()
            if otp is None:
                return Response({'data': 'unmatched'}, status=status.HTTP_201_CREATED)
                # return Response({'error': 'OTP not found'}, status=status.HTTP_404_NOT_FOUND)
            elif forget:
                otp.delete() 
                return Response({'data': 'matched'}, status=status.HTTP_201_CREATED) 
            else:
                data = {'email':otp.email,'mobile':otp.mobile,'password':otp.password,'username':otp.username}
                if OfflinePurchase.objects.filter(customer_email=email).exists() or OfflinePurchase.objects.filter(customer_contact_number=otp.mobile).exists():
                    data['subscription'] = True
                else:
                    data['subscription'] = False
                serializer = UserSerializer(data=data,partial=True)
                if serializer.is_valid():
                    raw_password = serializer.validated_data.get('password')
                    encrypted_password = encrypt_password(raw_password)
                    serializer.save(password=encrypted_password)
                    otp.delete()
                    return Response({'data': 'matched'}, status=status.HTTP_201_CREATED)
                else:
                    print(serializer.errors)
                    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                  
        except Exception as e:
            print(f"Error: {str(e)}") 
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SignIn(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get("email")
            password = data.get("password")
            if User.objects.filter(email=email,inactive=True).exists():
                return Response({'data': 'inactive_user'},status=status.HTTP_200_OK)
            user = User.objects.get(email=email,inactive=False)
            encryptPassword = encrypt_password(password) 
            if OfflinePurchase.objects.filter(customer_email=email).exists() or OfflinePurchase.objects.filter(customer_contact_number=user.mobile).exists():
                    user.subscription = True
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
                        "data": {"user_id":user.id,'username':user.username, "subscription":user.subscription},  
                        "message": "User logged in successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(e)
            return Response({"message": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

# class SignIn(APIView):
#     def post(self, request):
#         try:
#             data = request.data
#             email = data.get("email")
#             password = data.get("password")
#             user = User.objects.get(email=email)
#             encryptPassword = encrypt_password(password) 
#             if OfflinePurchase.objects.filter(customer_email=email).exists() or OfflinePurchase.objects.filter(customer_contact_number=user.mobile).exists():
#                     user.subscription = True
#             if user.subscription:
#                 if user.role == 'visitor':
#                     user.role = 'purchasedUser'
#                     user.save()
#             if user.password == encryptPassword:
#                 if user.role == "purchasedUser":
#                     token = purchasedUser_encode_token({"id": str(user.id), "role": user.role})
#                 elif user.role == "CourseSubscribedUser":
#                     token = courseSubscribedUser_encode_token({"id": str(user.id), "role": user.role})
#                 elif user.role == "admin":
#                     token = admin_encode_token({"id": str(user.id), "role": user.role})
#                 elif user.role == "visitor":
#                     token = visitor_encode_token({"id": str(user.id), "role": user.role})
#                 else:
#                     return Response(
#                         {"message": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST
#                     )
                
#                 refresh = RefreshToken.for_user(user)
#                 return Response(
#                     {
#                         "token": str(token),
#                         "access": str(refresh.access_token),
#                         "data": {"user_id":user.id,'username':user.username, "subscription":user.subscription},  
#                         "message": "User logged in successfully",
#                     },
#                     status=status.HTTP_200_OK,
#                 )
#             return Response(
#                 {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         except User.DoesNotExist:
#             return Response(
#                 {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(e)
#             return Response({"message": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

class Forget(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            if User.objects.filter(email=email,inactive=False).exists():
                otp = generate_otp()
                otp_record = OTP.objects.filter(email=email).first()
                if otp_record:
                        otp_record.otp = otp
                        otp_record.save()
                else:
                    otp_data = {'email': email, 'otp': otp}
                    otp_save = OTPSerializer(data=otp_data,partial=True)
                    if otp_save.is_valid():
                        otp_save.save()
                    else:
                        return Response(otp_save.errors, status=status.HTTP_400_BAD_REQUEST)

                send_mail(
                    'Reset Your Password',
                    f"""
                    Dear User,

                    We received a request to reset your password.

                    To reset your password, please use the following One-Time Password (OTP) on the reset page:

                    Your OTP is: {otp}

                    If you did not request a password reset, please ignore this email and your password will remain unchanged.

                    Thank you for using our services!  
                    If you have any questions, feel free to reach out to us at info@mi-bot.com.

                    Best regards,  
                    The MiBOT Ventures Team
                    """,
                    os.getenv('EMAIL_HOST_USER'),
                    [email],
                    fail_silently=False
                )

                datas = {'email': email, 'isexists': 'yes'}
                return Response({'data': datas, 'message': "Mail sent successfully"}, status=status.HTTP_201_CREATED)
            else:
                data = {'email': email, 'isexists': 'no'}
                return Response({'data': data, 'message': "Unsuccessful, try again"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UpdatePassword(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            user = User.objects.filter(email=email).first()
            if user:
                user.password = encrypt_password(password)
                user.save()
                return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UploadCourse(APIView):
    def post(self, request):
        try:
            data = self.request.data
            course_serializer = CourseSerializer(data=data)
            if course_serializer.is_valid():
                course_instance = course_serializer.save()  
                serialized_course = CourseSerializer(course_instance).data
                logger.info("Course created successfully")
                print(serialized_course)
                return Response({'data': serialized_course, 'message': "Course created successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': course_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({'error': 'Something went wrong while uploading data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, request, *args, **kwargs):
        try:
            courses = Course.objects.filter(status=False)
            if courses.exists():
                course_serializer = CourseSerializer(courses, many=True)
                return Response({'data': course_serializer.data, 'message': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({'data': 'empty', 'message': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({'error': 'Something went wrong while uploading data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UploadModule(APIView):
    def post(self, request):
        try:
            data = self.request.data
            files = self.request.FILES  # Uploaded files
            course = Course.objects.get(id=data['course'])

            # Initialize URLs as None
            overview_url = None
            content_url = None
            activity_url = None

            # Get uploaded files
            content_file = files.get('content')  
            intro_file = files.get('intro')
            activity_file = files.get('activity')

            if content_file and intro_file and activity_file:
                # Extract file extensions
                ex1 = os.path.splitext(content_file.name)[1]
                ex2 = os.path.splitext(intro_file.name)[1]
                ex3 = os.path.splitext(activity_file.name)[1]

                if ex1 in ['.pptx', '.ppt']:
                    content_result = upload(content_file, resource_type='raw')  # Upload to cloud storage
                    content_url = content_result['secure_url']
                elif ex1 == '.pdf':
                    content_url = default_storage.save(content_file.name, content_file)  # Save locally
                if ex2 in ['.pptx', '.ppt']:
                    overview_result = upload(intro_file, resource_type='raw')  # Upload to cloud storage
                    overview_url = overview_result['secure_url']
                elif ex2 == '.pdf':
                    overview_url = default_storage.save(intro_file.name, intro_file)  # Save locally
                if ex3 in ['.pptx', '.ppt']:
                    activity_result = upload(activity_file, resource_type='raw')  # Upload to cloud storage
                    activity_url = activity_result['secure_url']
                elif ex3 == '.pdf':
                    activity_url = default_storage.save(activity_file.name, activity_file)  # Save locally

                module = Module.objects.create(
                    module_name=data['module_name'],
                    module_description=data['module_description'],
                    intro=overview_url,
                    content=content_url,
                    activity=activity_url,
                    course=course
                )
                
                serializer = ModuleSerializer(module)
                return Response({'data': serializer.data, 'message': "Module created Successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'All required files (content, intro, activity) must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error: {str(e)}") 
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, *args, **kwargs):
        try:
            # Extract data from the request
            data = request.data
            id = data.get('id')
            files = request.FILES
            extension = data.get('extension', '').lower()
            url = None
            file = files.get('file')

            # Fetch the module object by ID
            module = Module.objects.get(id=id)

            if file:
             # Handle PowerPoint and PDF file uploads
                if extension in ['pptx', 'ppt']:
                 content_result = upload(file, resource_type='raw')  # Upload to cloud storage (Cloudinary)
                 url = content_result['secure_url']
                elif extension == 'pdf':
                 # Save the PDF file to local storage
                 url = default_storage.save(file.name, file)

            if url:
             # Handle module content type update (content, overview, or activity)
                if data.get('type') == 'content':
                 delete_existing_file(module.content)  
                 module.content = url
                elif data.get('type') == 'overview':
                    delete_existing_file(module.intro)  
                    module.intro = url
                elif data.get('type') == 'activity':
                    delete_existing_file(module.activity)  # Use helper function
                    module.activity = url

            # Save the updated module
            module.save()

            # Serialize the updated module and return the response
            serializer = ModuleSerializer(module, partial=True)
            return Response({'data': serializer.data, 'message': "Module updated successfully"}, status=status.HTTP_200_OK)

        except Module.DoesNotExist:
         return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AssessmentQuestion(APIView):
    def post(self,request):
        try:
            data = self.request.data
            assess = AssessmentSerializer(data = data)
            if assess.is_valid():
                assess.save()
                return Response({'data': assess.data, 'message': "assessment created Successfully"}, status=status.HTTP_201_CREATED)
            else:
                print(f"Validation errors: {assess.errors}")
                return Response({'error': assess.errors}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

class FetchCoursePreview(APIView):
    def post(self, request):
        try:
            data = request.data
            print("Received data:", data) 
            course_id = data.get('courseid')
            if not course_id:
                return Response({'error': 'courseid not provided'}, status=status.HTTP_400_BAD_REQUEST)

            course = Course.objects.get(id=course_id)

            course_data = {
                'id': str(course.id),
                'course_name': course.course_name,
                'course_description': course.course_description,
                'course_duration': course.course_duration,
                'video':course.video,
                'isconfirmed': course.status,
                'course_cover_image': course.course_cover_image.url,
                'modules': []
            }

            modules = Module.objects.filter(course=course)
            for module in modules:
                # Determine file types based on file extensions
                type_intro = os.path.splitext(module.intro.name)[1] if module.intro else None
                type_content = os.path.splitext(module.content.name)[1] if module.content else None
                type_activity = os.path.splitext(module.activity.name)[1] if module.activity else None

                # Ensure we return URLs for all file types, including PPT files
                intro_urls = module.intro.url if module.intro else None
                content_urls = module.content.url if module.content else None
                activity_urls = module.activity.url if module.activity else None

                if type_intro in ['.ppt', '.pptx']:
                    intro_urls = f"https://view.officeapps.live.com/op/embed.aspx?src={module.intro}"
                else:
                    intro_urls = module.intro.url if module.intro else None

                if type_content in ['.ppt', '.pptx']:
                    content_urls = f"https://view.officeapps.live.com/op/embed.aspx?src={module.content}"
                else:
                    content_urls = module.content.url if module.content else None

                if type_activity in ['.ppt', '.pptx']:
                    activity_urls = f"https://view.officeapps.live.com/op/embed.aspx?src={module.activity}"
                else:
                    activity_urls = module.activity.url if module.activity else None

                module_data = {
                    'id': str(module.id),
                    'module_name': module.module_name,
                    'module_description': module.module_description,
                    'intro': intro_urls,
                    'type_intro': type_intro,
                    'content': content_urls,
                    'type_content': type_content,
                    'activity': activity_urls,
                    'type_activity': type_activity,
                    'assessments': []
                }

                assessments = Assessment.objects.filter(module=module.id)
                for assessment in assessments:
                    assessment_data = {
                        'id': str(assessment.id),
                        'question': assessment.question,
                        'options': [assessment.option1, assessment.option2, assessment.option3, assessment.option4],
                        # 'answer': assessment.answer,
                    }
                    module_data['assessments'].append(assessment_data)

                course_data['modules'].append(module_data)

            print(course_data)
            return Response({'data': course_data}, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class canviewmodule(APIView):
    def get(self, request, *args, **kwargs):
        try:
            userid = request.query_params.get('userid')
            modid = request.query_params.get('moduleid')
            assessscore = UserAssessmentScore.objects.filter(user=userid,module=modid).first()
            if assessscore:
                per = (assessscore.obtained_marks/assessscore.total_marks)*100
                if(per<65):
                    return Response({'data': 'unallow'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    return Response({'data': 'allow'}, status=status.HTTP_200_OK)
            else:
                print(assessscore)
                return Response({'data': 'unallow'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class tasktrack(APIView):
    def post(self,request):
        try:
            data = request.data
            userid = data.get('userid')
            courseid = data.get('courseIds')
            modid = data.get('moduleid')
            tasks = data.get('task')
            # image = data.get('image')
            # Check if UserCourseProgress already exists
            isfound = UserCourseProgress.objects.filter(user=userid, course=courseid).first()
            if(modid):
                # Retrieve the Module instance for last_module
                module_instance = get_object_or_404(Module, id=modid)
                insideassessment = UserAssessmentScore.objects.filter(module=modid)
                if isfound:
                    # Update the existing instance
                    if(isfound.last_module != module_instance):
                        isfound.last_module = module_instance
                        isfound.content = 0
                        isfound.activity = 0
                    isfound.task = tasks
                    if(insideassessment):
                        isfound.content = 1
                        isfound.activity = 1
                    else:
                        if(tasks == 'main'):
                            isfound.content = 1
                        elif(tasks == 'activity'):
                            if(isfound.content == 1):
                                isfound.activity = 1
                    isfound.updated_at = timezone.now()
                    isfound.save()
                    data = {'main':isfound.content,'activity':isfound.activity}
                    return Response({'data': data}, status=status.HTTP_200_OK)
                else:
                    # If not found, create a new UserCourseProgress record
                    data = {'user': userid, 'course': courseid, 'last_module': module_instance.id, 'task': tasks}
                    track = TasktrackSerializer(data=data)
                    if track.is_valid():
                        track.save()
                        return Response({'data': 'progress created'}, status=status.HTTP_201_CREATED)
                    else:
                        print(track.errors)
                        return Response(track.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                if isfound:
                     # Update the existing instance
                    isfound.last_module = None
                    isfound.task = tasks
                    isfound.updated_at = timezone.now()
                    isfound.save()
                    return Response({'data': 'progress updated'}, status=status.HTTP_200_OK)
                else:
                    # If not found, create a new UserCourseProgress record
                    data = {'user': userid, 'course': courseid, 'last_module': None, 'task': tasks}
                    track = TasktrackSerializer(data=data)
                    if track.is_valid():
                        track.save()
                        return Response({'data': 'progress created'}, status=status.HTTP_201_CREATED)
                    else:
                        print(track.errors)
                        return Response(track.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get('userid')
            course_id = request.query_params.get('courseid')
            progress = UserCourseProgress.objects.filter(user=user_id, course=course_id).first()
            if progress:
                serialized_progress = TasktrackSerializer(progress)
                last_mod_id = serialized_progress.data.get('last_module')
                if last_mod_id:

                    track = serialized_progress.data.get('task')
                    module = Module.objects.get(id=last_mod_id)
                    type_intro = os.path.splitext(module.intro.name)[1] if module.intro else None
                    type_content = os.path.splitext(module.content.name)[1] if module.content else None
                    type_activity = os.path.splitext(module.activity.name)[1] if module.activity else None

                    # Ensure we return URLs for all file types, including PPT files
                    intro_urls = module.intro.url if module.intro else None
                    content_urls = module.content.url if module.content else None
                    activity_urls = module.activity.url if module.activity else None

                    if type_intro in ['.ppt', '.pptx']:
                        intro_urls = f"https://view.officeapps.live.com/op/embed.aspx?src={module.intro}"
                    else:
                        intro_urls = module.intro.url if module.intro else None

                    if type_content in ['.ppt', '.pptx']:
                        content_urls = f"https://view.officeapps.live.com/op/embed.aspx?src={module.content}"
                    else:
                        content_urls = module.content.url if module.content else None

                    if type_activity in ['.ppt', '.pptx']:
                        activity_urls = f"https://view.officeapps.live.com/op/embed.aspx?src={module.activity}"
                    else:
                        activity_urls = module.activity.url if module.activity else None

                    module_data = {
                        'id': str(module.id),
                        'module_name': module.module_name,
                        'module_description': module.module_description,
                        'intro': intro_urls,
                        'type_intro': type_intro,
                        'content': content_urls,
                        'type_content': type_content,
                        'activity': activity_urls,
                        'type_activity': type_activity,
                        'task': track,
                        'assessments': []
                    }

                    assessments = Assessment.objects.filter(module=module.id)
                    for assessment in assessments:
                        assessment_data = {
                            'id': str(assessment.id),
                            'question': assessment.question,
                            'options': [assessment.option1, assessment.option2, assessment.option3, assessment.option4],
                        }
                        module_data['assessments'].append(assessment_data)

                    return Response({'data': module_data}, status=status.HTTP_200_OK)
                
                else:
                    serialized_progress = TasktrackSerializer(progress)
                    track = serialized_progress.data.get('task')
                    return Response({'data': track}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class pickup(APIView):
    def get(self, request):
        try:
            user_id = request.query_params.get('user')
            print(user_id)
            if not user_id:
                return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            progress = UserCourseProgress.objects.filter(user=user_id).order_by('-updated_at').first()
            if progress:
                serialized_progress = TasktrackSerializer(progress)
                course_id = str(serialized_progress.data.get('course'))
                course = Course.objects.filter(id=course_id).first()
                image = course.course_cover_image.url  
        
                data = {
                    'course': serialized_progress.data.get('course'),
                    'user': serialized_progress.data.get('user'),
                    'module': serialized_progress.data.get('last_module'),
                    'image': image,
                }
                return Response({'data': data}, status=status.HTTP_200_OK)

            return Response({'error': 'No progress found for this user'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class courseconfirm(APIView):
    def post(self,request):
        try:
            data = request.data
            course_id = data.get('courseid')
            course = Course.objects.get(id=course_id)
        
            if course:
                if(course.isconfirmed):
                    course.isconfirmed = False
                else:
                    course.isconfirmed = True
                course.save()
                return Response({'message': 'confirmed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'course not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class courselist(APIView):
    def get(self, request, *args, **kwargs):
        try:
            courselists = Course.objects.filter(status=True)
            serializer = CourseSerializer(courselists, many=True)
            data = serializer.data 
            print(data)
            enriched_data = []  
            for each in data:
                product = Product.objects.get(id=each['product'])
                category = Category.objects.get(id=product.category.id)  # Use .id to get the UUID
                modules = Module.objects.filter(course=each['id'])
                each['module_count'] = modules.count()  
                each['category'] = category.category_name  
                enriched_data.append(each) 

            print(enriched_data)
            return Response({'data': enriched_data, 'message': 'confirmed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CourseListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            print("Query Parameters:", request.query_params)

        # Query courses with status=True
            queryset = Course.objects.filter(status=True)
        
        # Apply filters using the filterset
            filterset = CourseFilter(request.query_params, queryset=queryset)
        
            if filterset.is_valid():
                queryset = filterset.qs  # Filter the queryset
                print("Filtered Queryset:", queryset)
            else:
                print("Filter errors:", filterset.errors)

        # Serialize the filtered queryset
            serializer = CourseFilterSerializer(queryset, many=True)
            enriched_data = [] 
            data = serializer.data
            for each in data:
                    product = Product.objects.get(id=each['product'])
                    category = Category.objects.get(id=product.category.id)  # Use .id to get the UUID
                    modules = Module.objects.filter(course=each['id'])
                    each['module_count'] = modules.count()  
                    each['category'] = category.category_name  
                    enriched_data.append(each) 

            print(enriched_data)
            return Response({'data': enriched_data, 'message': 'confirmed successfully'}, status=status.HTTP_200_OK)
        # return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductView(APIView):
    def get(self, request, *args, **kwargs):
        print("Query Parameters:", request.query_params)

        # Query courses with status=True
        queryset = Product.objects.all()
        
        # Apply filters using the filterset
        filterset = ProductFilter(request.query_params, queryset=queryset)
        
        if filterset.is_valid():
            queryset = filterset.qs  # Filter the queryset
            print("Filtered Queryset:", queryset)
        else:
            print("Filter errors:", filterset.errors)

        # Serialize the filtered queryset
        serializer = ProductSerializer(queryset, many=True)
        enriched_data = [] 
        data = serializer.data
        for each in data:
                category = Category.objects.get(id=each['category']) 
                each['category'] = category.category_name  
                enriched_data.append(each) 

        return Response({'data': enriched_data, 'message': 'confirmed successfully'}, status=status.HTTP_200_OK)
        # return Response({"data": serializer.data}, status=status.HTTP_200_OK)

class Eachproduct(APIView):
    def get(self, request):
        id = request.query_params.get('productid')
        product = Product.objects.filter(id=id).first()
        serializer = ProductSerializer(product)
        data = serializer.data
        category = Category.objects.filter(id=data['category']).first()
        cat_serializer = CategorySerializer(category)  # Serialize the category
        data['category'] = cat_serializer.data  # Assign serialized category data to the response
        print(data)
        return Response({'data': data, 'message': 'confirmed successfully'}, status=status.HTTP_200_OK)

        
class addproduct(APIView):
    # def post(self, request):
    #     try:
    #         data = self.request.data
    #         product_serializer = ProductSerializer(data=data)
    #         if product_serializer.is_valid():
    #             product_instance = product_serializer.save()  
    #             serialized_product = ProductSerializer(product_instance).data
    #             logger.info("Product created successfully")
    #             print(serialized_product)
    #             return Response({'data': serialized_product, 'message': "Product created successfully"}, status=status.HTTP_201_CREATED)
    #         else:
    #             return Response({'error': product_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         logger.error(f"Error occurred: {e}")
    #         return Response({'error': 'Something went wrong while uploading data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        print(request.data)
        serializer = ProductSerializer(data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        logger.error(serializer.errors)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, *args, **kwargs):
        try:
            product = Product.objects.all()
            product_serializer = ProductSerializer(product, many=True)
            print(product_serializer.data)
            return Response({'data': product_serializer.data, 'message': "Products fetched successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
        
class OfflinePurchaseUserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            id = request.data.get('id')
            password = request.data.get('password')
            user = User.objects.filter(id=id).first()  

            # Check if the user exists
            if user is None:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the password matches
            if user.password == encrypt_password(password):
                data = request.data
                serializer = OfflinePurchaseSerializer(data=data)

                if serializer.is_valid():
                    serializer.save()
                    return Response({'data': serializer.data, 'message': "Offline purchase created successfully"}, 
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Wrong password'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, pk, *args, **kwargs):
        data = request.data
        offline_purchase = OfflinePurchase.objects.get(pk=pk)
        serializer = OfflinePurchaseSerializer(offline_purchase, data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data, 'message': "Offline purchase updated successfully"})
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, pk, *args, **kwargs):
        offline_purchase = OfflinePurchase.objects.get(pk=pk)
        serializer = OfflinePurchaseSerializer(offline_purchase)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
    def delete(self, request, pk, *args, **kwargs):
        offline_purchase = OfflinePurchase.objects.get(pk=pk)
        offline_purchase.delete()
        return Response({'message': 'Offline purchase deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
class getdetails(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get('id')
            if not user_id:
                return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = UserdetailsSerializer(user)
            return Response({'data': serializer.data, 'message': 'success'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class checkanswers(APIView):
    def post(self, request):
        try:
            modid = request.data.get('moduleId')
            answers = request.data.get('answers')
            userid = request.data.get('userid')
            courseid = request.data.get('courseId')
            count = 0
            total = 0
            results = [] 
            for task_id, selected_option in answers.items():  
                assessment = Assessment.objects.filter(id=task_id).first()
                total = total + 1
                if assessment:
                    if assessment.answer == selected_option:
                        results.append({task_id: 'correct'})
                        count = count + 1
                    else:
                        results.append({task_id: 'wrong'})
                else:
                    results.append({task_id: 'not found'})
            per = (count/total)*100
            results.append({'percentage':per})
            user = UserAssessmentScore.objects.filter(user = userid,module = modid).first()
            if user:
                user.obtained_marks = count
                user.total_marks = total
                user.save()
                print(results)
                return Response({'data': results, 'message': 'success'}, status=status.HTTP_200_OK)
            else:
                data = {'module':modid,'total_marks':total,'obtained_marks':count,'user':userid,'course':courseid}
                serialiser = UserAssessmentSerialiser(data = data)
                if serialiser.is_valid():
                    serialiser.save()
                    print(results)
                    return Response({'data': results, 'message': 'success'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': serialiser.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class checkcertifyanswer(APIView):
    def post(self,request):
        try:
            courseid = request.data.get('courseid')
            answers = request.data.get('answers')
            userid = request.data.get('userid')
            certification = Certification.objects.filter(course=courseid).first()
            count = 0
            total = 0
            results = [] 
            for task_id, selected_option in answers.items():  
                certifydata = CertificationQuestion.objects.filter(id=task_id).first()
                print(certifydata)
                total = total + 1
                if certifydata:
                    if certifydata.answer == selected_option:
                        results.append({task_id: 'correct'})
                        count = count + 1
                    else:
                        results.append({task_id: 'wrong'})
                else:
                    results.append({task_id: 'not found'})
            per = (count/total)*100
            results.append({'percentage':per})
            usercertify = UserCertificationScore.objects.filter(user = userid,certify = certification.id).first()
            if usercertify:
                usercertify.obtained_marks = count
                usercertify.total_marks = total
                usercertify.save()
                print(results)
                return Response({'data': results, 'message': 'success'}, status=status.HTTP_200_OK)
            else:
                data = {'certify':certification.id,'total_marks':total,'obtained_marks':count,'user':userid,'course':courseid}
                serialiser = UserCertificationSerialiser(data = data)
                if serialiser.is_valid():
                    serialiser.save()
                    print(results)
                    return Response({'data': results, 'message': 'success'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': serialiser.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class updatedetails(APIView):
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('id')
            print("Received data:", data)
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Use the serializer for a partial update
            serializer = UserdetailsSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'data': serializer.data, 'message': 'User updated successfully'}, status=status.HTTP_200_OK)
            
            print("Serializer errors:", serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Error details:", str(e))  
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class canaccesscourse(APIView):
    def get(self, request):
        try:
            id = request.query_params.get('userid')
            user = User.objects.filter(id=id).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if user.role in ['purchasedUser', 'CourseSubscribedUser', 'admin']:
                return Response({'data': 'allow'}, status=status.HTTP_200_OK)
            else:
                return Response({'data': 'unallow'}, status=status.HTTP_200_OK) 

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StatisticsAPIView(APIView):
    
    def get(self, request):
        # User statistics
        total_users = User.objects.count()
        purchased_users = User.objects.filter(role='purchasedUser').count()
        subscribed_users = User.objects.filter(role='CourseSubscribedUser').count()
        # subscribed_users = User.objects.filter(subscription=True).count()
        users_by_role = User.objects.values('role').annotate(count=Count('role'))

        # Offline Purchase statistics
        total_purchases = OfflinePurchase.objects.count()
        purchases_by_product = OfflinePurchase.objects.values('product_name').annotate(count=Count('product_name'))
        revenue_by_product = OfflinePurchase.objects.values('product_name').annotate(revenue=Sum('product_price'))
        purchases_by_payment_method = OfflinePurchase.objects.values('payment_term').annotate(count=Count('payment_term'))

        # Course statistics
        total_courses = Course.objects.count()
        courses_by_level = Course.objects.values('level').annotate(count=Count('level'))
        courses_by_age_category = Course.objects.values('age_category').annotate(count=Count('age_category'))
        courses_by_product = Course.objects.values('product_model').annotate(count=Count('product_model'))

        # Preparing data for the serializer
        data = {
            'total_users': total_users,
            'purchased_users': purchased_users,
            'subscribed_users': subscribed_users,
            'users_by_role': {item['role']: item['count'] for item in users_by_role},

            'total_purchases': total_purchases,
            'purchases_by_product': {item['product_name']: item['count'] for item in purchases_by_product},
            'revenue_by_product': {item['product_name']: item['revenue'] for item in revenue_by_product},
            'purchases_by_payment_method': {item['payment_term']: item['count'] for item in purchases_by_payment_method},

            'total_courses': total_courses,
            'courses_by_level': {item['level']: item['count'] for item in courses_by_level},
            'courses_by_age_category': {item['age_category']: item['count'] for item in courses_by_age_category},
            'courses_by_product': {item['product_model']: item['count'] for item in courses_by_product},
        }

        print(data)
        return Response({"data": data}, status=status.HTTP_200_OK)
    
class DeleteModuleView(APIView):
    def delete(self, request, id):
        try:
            # Retrieve the module by its ID
            module = Module.objects.get(id=id)

            # List of file fields in the Module model to check and delete
            file_fields = ['intro', 'content', 'activity']

            for field in file_fields:
                file_field = getattr(module, field)

                # If there's a file in the field
                if file_field:
                    file_url = file_field.url
                    if file_url.endswith('.pdf'):
                        # Delete PDF from default storage
                        if default_storage.exists(file_field.name):
                            default_storage.delete(file_field.name)
                        else:
                            print(f"PDF file not found in storage: {file_url}")

                    elif file_url.endswith(('.ppt', '.pptx')):
                        # Delete PowerPoint files from Cloudinary
                        # public_id = file_url.split('/')[-1].split('.')[0]  # Extract Cloudinary public ID
                        path_parts = file_url.split('/')
                        public_id = path_parts[-1]
                        print(f"Deleting Cloudinary file with public_id: {public_id}")
                        result = cloudinary.uploader.destroy(public_id, resource_type="raw")
                        print(f"Cloudinary deletion result: {result}")
                    else:
                        print(f"Unsupported file type for deletion: {file_url}")

            # Delete the module from the database
            module.delete()

            return Response({'message': 'Module and associated files deleted successfully'}, status=status.HTTP_200_OK)

        except Module.DoesNotExist:
            return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
class deleteQuestion(APIView):
    def delete(self, request, id):
        try:
            assess = Assessment.objects.get(id=id)
            assess.delete()
            return Response({'message': 'deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class deleteCourse(APIView):
    def delete(self, request, id):
        try:
            course = Course.objects.get(id=id)

            # Helper function to delete files conditionally
            def delete_file(file_field):
                if file_field:
                    file_path = file_field.path
                    file_extension = file_path.split('.')[-1].lower()

                    # Check if the file is a PDF
                    if file_extension == "pdf":
                        default_storage.delete(file_path)

                    # Check if the file is a PPT or PPTX and delete from Cloudinary
                    elif file_extension in ["ppt", "pptx"]:
                        path_parts = file_path.split('/')
                        public_id = path_parts[-1]
                        print(f"Deleting Cloudinary file with public_id: {public_id}")
                        result = cloudinary.uploader.destroy(public_id, resource_type="raw")
                        print(f"Cloudinary deletion result: {result}")
                    else:
                        default_storage.delete(file_path)

            # Delete the course cover image from default storage
            if course.course_cover_image:
                delete_file(course.course_cover_image)

            # Delete files in each module related to the course
            for module in course.modules.all():
                delete_file(module.intro)
                delete_file(module.content)
                delete_file(module.activity)

            # Delete the course record
            course.delete()

            return Response({'message': 'Deleted successfully'}, status=status.HTTP_200_OK)
        
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class CertificationAPIViews(APIView):
    def get(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id', None)
        if course_id:
            certifications = Certification.objects.filter(course_id=course_id)
            serializer = CertificationsSerializer(certifications, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "Course ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        print(request.data)
    
        course_id = request.data.get('course_id')
        certification_data = request.data.get('certification')
        if not course_id:
            return Response({"error": "Course ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not certification_data:
            return Response({"error": "Certification data is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Fetch the course by ID
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        
        print(course)
        # Prepare data for certification creation
        certification_data['course'] = course.id  # Associate course with certification

        # Serialize the certification data and pass the course in context
        serializer = CertificationsSerializer(data=certification_data, context={'course': course})
        
        if serializer.is_valid():
            # Save the certification and related questions
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        
        logger.error(serializer.errors)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class deletecertifyques(APIView):
    def delete(self, request, id, courseid):
        try:
            certifydel = CertificationQuestion.objects.get(id=id) 
            certifydel.delete()
            certifications = Certification.objects.filter(course_id=courseid)
            serializer = CertificationsSerializer(certifications, many=True)
            return Response({"data": serializer.data,'message': 'deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class CertificationUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            certification = Certification.objects.get(pk=pk)
            serializer = CertificationSerializer(certification, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Certification.DoesNotExist:
            return Response({"error": "Certification not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')
            amount = data.get('amount')
            currency = data.get('currency')
            receipt = data.get('receipt')
            # notes = data.get('notes')
            
            serializedTransaction = TransactionOrderSerializer(data=data)
            if serializedTransaction.is_valid():
                serializedTransaction.save()
                response = client.order.create(data={'amount': amount, 'currency': currency, 'receipt': receipt})
                response['user_id'] = user_id
                return Response({'data': response}, status=status.HTTP_200_OK)
            else:
                return Response({'error': serializedTransaction.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception:", str(e)) 
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CheckoutAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')
            razorpay_order_id = data.get('orderId')
            razorpay_payment_id = data.get('paymentId')
            razorpay_signature = data.get('signature')
            print(data)
            serializedTransaction = TransactionCheckOutSerializer(data=data)
            if(serializedTransaction.is_valid()):
                response = client.utility.verify_payment_signature({'razorpay_order_id': razorpay_order_id,'razorpay_payment_id': razorpay_payment_id, 'razorpay_signature': razorpay_signature})
                print(response)
                # Retrieve the Transaction object based on user_id
                transaction = get_object_or_404(Transaction, user_id=user_id)
                print(transaction)
                # Update transaction details
                transaction.razorpay_order_id = razorpay_order_id
                transaction.razorpay_payment_id = razorpay_payment_id
                transaction.razorpay_signature = razorpay_signature
                
                # Save the updated transaction
                transaction.save()
                print(transaction.razorpay_order_id)
                # Save the serialized data
                serializedTransaction.save()
                return Response({'data': {"response":response, "user_id":user_id}}, status=status.HTTP_200_OK)
            else:
                return Response({'error': serializedTransaction.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserReviews(APIView):
    def post(self, request):
        try:
            data = request.data
            if 'course' not in data or not data['course']:
                return Response({'error': 'Course ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            course = Course.objects.filter(id=data['course']).first()
            if not course:
                return Response({'error': 'Invalid course ID.'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserReviewSerializer(data=data)
            if serializer.is_valid():
                review_data = serializer.save()
                review_data_list = UserReview.objects.filter(course=review_data.course)
                reviews_list = []
                rating_sum = 0

                for review in review_data_list:
                    reviewer = User.objects.get(id=review.user.id)
                    reviews_list.append({
                        'username': reviewer.username,
                        'rating': review.rating,
                        'review': review.review,
                        'createdAt': review.created_at
                    })
                    rating_sum += review.rating
                
                rating_avg = rating_sum / len(reviews_list)
                course.rating = rating_avg
                course.save()
                
                return Response({'data': reviews_list}, status=status.HTTP_200_OK)
            else:
                print("Serializer errors:", serializer.errors)  
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            course_id = request.query_params.get('id')
        
            if not course_id:
                return Response({'error': 'Course ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            review_data = UserReview.objects.filter(course=course_id)
            reviews_list = []

            for review in review_data:
                reviews_list.append({
                    'username': review.user.username,  
                    'rating': review.rating,
                    'review': review.review,
                    'createdAt': review.created_at
                })

            return Response({'data': reviews_list}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# class UserCourses(APIView):

#     def get(self, request):
#         try:
#             user_id = request.query_params.get('id')
#             print(user_id)
#             if not user_id:
#                 return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)

#             # Initialize response data
#             completed = 0
#             completed_module = 0
#             ongoing_courses = []

#             # Fetch data for the user
#             course_data = UserCourseProgress.objects.filter(user=user_id)
#             certification_data = UserCertificationScore.objects.filter(user=user_id)

#             if course_data:
#                 courses_started = len(course_data)
#                 for courses in course_data:
#                     course_id = courses.course.id
#                     if not course_id:
#                         continue  # Skip invalid course IDs

#                     # Fetch course details
#                     course = Course.objects.filter(id=course_id).first()
#                     if not course:
#                         continue  # Skip non-existent courses

#                     # Fetch modules and user assessments
#                     module = Module.objects.filter(course=course)
#                     total_module_count = len(module)

#                     userassess = UserAssessmentScore.objects.filter(user=user_id, course=course)
#                     completed_module = 0
#                     for module_completed in userassess:
#                         per = (module_completed.obtained_marks / module_completed.total_marks) * 100
#                         if per >= 65:
#                             completed_module += 1

#                     ongoing_courses.append({
#                         'course_id': course_id,
#                         'course_image': course.course_cover_image.url if course.course_cover_image else None,
#                         'course_name': course.course_name,
#                         'total_module': total_module_count,
#                         'completed_module': completed_module
#                     })

#             if certification_data:
#                 for certify in certification_data:
#                     per = (certify.obtained_marks / certify.total_marks) * 100
#                     if per >= 65:
#                         completed += 1
#             user = User.objects.filter(id=user_id).first()
#             # Construct response
#             datas = {
#                 'completed_course_count': completed,
#                 'course_started':courses_started,
#                 'name':user.username,
#                 'profiles': user.profile.url,
#                 'ongoing_courses': ongoing_courses
#             }
#             return Response({'data': datas}, status=status.HTTP_200_OK)

#         except Exception as e:
#             print("Exception:", str(e))
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserCourses(APIView):

    def get(self, request):
        try:
            user_id = request.query_params.get('id')
            print(user_id)
            if not user_id:
                return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)

            # Initialize response data
            completed = 0
            completed_module = 0
            ongoing_courses = []

            # Fetch data for the user
            course_data = UserCourseProgress.objects.filter(user=user_id)
            certification_data = UserCertificationScore.objects.filter(user=user_id)

            courses_started = 0
            if course_data:
                courses_started = len(course_data)
                for courses in course_data:
                    course_id = courses.course.id
                    if not course_id:
                        continue  # Skip invalid course IDs

                    # Fetch course details
                    course = Course.objects.filter(id=course_id).first()
                    if not course:
                        continue  # Skip non-existent courses

                    # Fetch modules and user assessments
                    module = Module.objects.filter(course=course)
                    total_module_count = len(module)

                    userassess = UserAssessmentScore.objects.filter(user=user_id, course=course)
                    completed_module = 0
                    for module_completed in userassess:
                        per = (module_completed.obtained_marks / module_completed.total_marks) * 100
                        if per >= 65:
                            completed_module += 1

                    ongoing_courses.append({
                        'course_id': course_id,
                        'course_image': course.course_cover_image.url if course.course_cover_image else None,
                        'course_name': course.course_name,
                        'total_module': total_module_count,
                        'completed_module': completed_module
                    })

            if certification_data:
                for certify in certification_data:
                    per = (certify.obtained_marks / certify.total_marks) * 100
                    if per >= 65:
                        completed += 1

            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if profile exists and has an associated file
            profile_url = None
            if user.profile and hasattr(user.profile, 'url'):
                try:
                    profile_url = user.profile.url  # Attempt to access the URL
                except ValueError:
                    profile_url = None  # Handle case where no file is associated

            # Construct response
            datas = {
                'completed_course_count': completed,
                'course_started': courses_started,
                'name': user.username,
                'profile': profile_url,
                'ongoing_courses': ongoing_courses
            }
            return Response({'data': datas}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class delaccount(APIView):
#     def post(self, request):
#         try:
#             data = request.data
#             id = data.get('id')
#             reason = data.get('reason')
#             serializer = delserialiser(data={'reason': reason})  # Ensure 'reason' is passed as a dictionary

#             if serializer.is_valid():
#                 serializer.save()
#                 delacc = User.objects.get(id=id) 
#                 delacc.delete()
#                 return Response({"data": 'success', 'message': 'Deleted successfully'}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
#         except User.DoesNotExist:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class delaccount(APIView):
    def post(self, request):
        try:
            data = request.data
            id = data.get('id')
            reason = data.get('reason')
            serializer = delserialiser(data={'reason': reason})  # Ensure 'reason' is passed as a dictionary

            if serializer.is_valid():
                serializer.save()
                delacc = User.objects.get(id=id) 
                # delacc['inactive'] = True;
                delacc.inactive = True  # Use attribute access instead of indexing
                # delacc.delete()
                delacc.save()
                return Response({"data": 'success', 'message': 'Deleted successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class categories(APIView):
    def get(self, request):
        try:
            cat = Category.objects.all()
            data = []
            for each in cat:
                data.append(each.category_name)  # Access category_name directly from each Category object
            print(data)
            return Response({'data': data, 'message': 'confirmed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class ProductReviews(APIView):
    def post(self, request):
        try:
            data = request.data
            
            product = Product.objects.filter(id=data['product']).first()
            if not product:
                return Response({'error': 'Invalid product ID.'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = Productreviewserialiser(data=data)
            if serializer.is_valid():
                review_data = serializer.save()
                review_data_list = ProductReview.objects.filter(product=review_data.product)
                reviews_list = []
                rating_sum = 0

                for review in review_data_list:
                    reviewer = User.objects.get(id=review.user.id)
                    reviews_list.append({
                        'username': reviewer.username,
                        'rating': review.rating,
                        'review': review.review,
                        'createdAt': review.created_at
                    })
                    rating_sum += review.rating
                
                rating_avg = rating_sum / len(reviews_list)
                product.rating = rating_avg
                product.save()
                
                return Response({'data': reviews_list}, status=status.HTTP_200_OK)
            else:
                print("Serializer errors:", serializer.errors)  
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            product_id = request.query_params.get('id')
        
            if not product_id:
                return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            review_data = ProductReview.objects.filter(product=product_id)
            reviews_list = []

            for review in review_data:
                reviews_list.append({
                    'username': review.user.username,  
                    'rating': review.rating,
                    'review': review.review,
                    'createdAt': review.created_at
                })

            return Response({'data': reviews_list}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductReviews(APIView):
    def post(self, request):
        try:
            data = request.data
            
            product = Product.objects.filter(id=data['product']).first()
            if not product:
                return Response({'error': 'Invalid product ID.'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = Productreviewserialiser(data=data)
            if serializer.is_valid():
                review_data = serializer.save()
                review_data_list = ProductReview.objects.filter(product=review_data.product)
                reviews_list = []
                rating_sum = 0

                for review in review_data_list:
                    reviewer = User.objects.get(id=review.user.id)
                    reviews_list.append({
                        'id':review.id,
                        'username': reviewer.username,
                        'rating': review.rating,
                        'review': review.review,
                        'createdAt': review.created_at
                    })
                    rating_sum += review.rating
                
                rating_avg = rating_sum / len(reviews_list)
                product.rating = rating_avg
                product.save()
                
                return Response({'data': reviews_list}, status=status.HTTP_200_OK)
            else:
                print("Serializer errors:", serializer.errors)  
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            product_id = request.query_params.get('id')
        
            if not product_id:
                return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            review_data = ProductReview.objects.filter(product=product_id)
            reviews_list = []

            for review in review_data:
                reviews_list.append({
                    'id':review.id,
                    'username': review.user.username,  
                    'rating': review.rating,
                    'review': review.review,
                    'createdAt': review.created_at
                })

            return Response({'data': reviews_list}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class delproductreview(APIView):
    def delete(self, request, id):
        try:
            productreviewdel = ProductReview.objects.get(id=id) 
            productreviewdel.delete()
            return Response({"data": 'success','message': 'deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionAmount(APIView):
    def get(self,request):
        try:
            data = SubscriptionMoney.objects.all().first()
            count = data.receiptcount
            count = count + 1
            data.receiptcount = count
            data.save()
            serialise = subscribeserialiser(data)
            return Response({'data': serialise.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class transact(APIView):
    def get(self, request):
        try:
            user = request.query_params.get('user_id')
            if not user:
                return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            data = Transaction.objects.filter(user_id=user)
            serialise = transactiondetails(data, many=True)
            print(serialise.data)
            return Response({'data': serialise.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class cartproduct(APIView):
    def post(self, request):
        try:
            data = request.data

            # Check if required fields are provided
            proid = data.get('product')
            user_id = data.get('user')
            if not proid or not user_id:
                return Response({'error': 'Product ID and User ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the product exists in the cart without a transaction
            cart_data = CartData.objects.filter(user=user_id,product=proid, transact=None).first()
            if cart_data:
                product = Product.objects.filter(id=cart_data.product.id).first()
                cart_data.quantity += 1
                cart_data.amount = cart_data.quantity * product.price
                cart_data.save()
                return Response({'data': 'success'}, status=status.HTTP_200_OK)
            else:
                serializer = cartserialiser(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'data': 'success'}, status=status.HTTP_200_OK)
                else:
                    print(serializer.errors)
                    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            user = request.query_params.get('user_id')
            if not user:
             return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            data = CartData.objects.filter(user_id=user, transact=None)
            serialdata = cartserial(data, many=True)

            # Iterate through the serialized data and replace the product field with serialized product data
            for datas in serialdata.data:
                product_id = datas['product']  # Access the product ID from the serialized data
                product = Product.objects.filter(id=product_id).first()
                if product:
                    serialproduct = ProductSerializer(product).data  # Serialize the product
                    datas['product'] = serialproduct  # Replace the product field with serialized product data

            print(serialdata.data)
            return Response({'data': serialdata.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        data = request.data
        cart_id = data.get('id')
        cart_type = data.get('type')
        
        # Fetch cart by id
        cart = CartData.objects.filter(id=cart_id).first()
        if not cart:
            return Response({'data': 'error', 'message': 'Cart item not found'}, status=404)
        product = Product.objects.filter(id=cart.product.id).first()
        if not product:
            return Response({'data': 'error', 'message': 'Product not found'}, status=404)
        
        if cart_type == 'sub':
            check = cart.quantity - 1
            if check > 0:
                cart.quantity -= 1
                cart.amount = cart.quantity * product.price
                cart.save()
                return Response({'data': 'success', 'message': 'Offline purchase updated successfully'})
            else:
                return Response({'data': 'error', 'message': 'Quantity cannot be less than 0'}, status=400)
        
        elif cart_type == 'add':
            if(product.stocks > cart.quantity):
                cart.quantity += 1
                cart.amount = cart.quantity * product.price 
                cart.save()
            return Response({'data': 'success'},status=200)
        
        return Response({'data': 'error', 'message': 'Invalid type'}, status=400)

class carttransact(APIView):
    def post(self, request):
        try:
            user_id = request.data.get('user')
            transact_id = request.data.get('transact')

            # Fetch the Transaction instance
            try:
                transaction = Transaction.objects.get(id=transact_id)
            except Transaction.DoesNotExist as e:
                print("Exception:", str(e))
                return Response({'error': 'Transaction does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the cart items belonging to the user
            cart_items = CartData.objects.filter(user=user_id, transact=None)
            if not cart_items.exists():
                return Response({'error': 'No cart items found for the user'}, status=status.HTTP_404_NOT_FOUND)

            # Update the transact field for cart items
            for item in cart_items:
                stockupdate = Product.objects.filter(id=item.product.id).first()
                stockupdate.stocks = stockupdate.stocks - item.quantity
                item.transact = transaction
                item.save()
                stockupdate.save()

            return Response({'data': 'Cart updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class delcart(APIView):
    def delete(self, request, id):
        try:
            carddel = CartData.objects.get(id=id) 
            carddel.delete()
            return Response({"data": 'success','message': 'deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
class getprodetail(APIView):
    def get(self,request):
        try:
            transacid = request.query_params.get('id')
            prodetail = []
            data = CartData.objects.filter(transact=transacid)
            for cartdata in data:
                product = Product.objects.filter(id=cartdata.product.id).first()
                datas = {
                    'product_name':product.product_name,
                    'price': product.price,
                    'quantity':cartdata.quantity,
                    'total':cartdata.amount
                }
                prodetail.append(datas)
            print(prodetail)
            return Response({'data': prodetail}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class buyerct(APIView):
    def get(self, request):
        try:
            userid = request.query_params.get('user')  
            data = CartData.objects.all()
            count = data.count()  
            print(count)
            return Response({'data': count}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class activates(APIView):
    def post(self,request):
        try:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            # user['inactive'] = False
            user.inactive = False;
            user.save()
            return Response({'data': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SendOTP(APIView):
    def post(self, request):
        try:
            mobile = request.data.get('mobile')
            password = request.data.get('password')
            email = request.data.get('email')
            username = request.data.get('username')
            type = request.data.get('type')
            otp_record = OTP.objects.filter(email=email).first()
            if type == 'send':
                if User.objects.filter(email=email,inactive=False).exists():
                    return Response({'data': 'email_found'}, status=status.HTTP_200_OK)
                elif User.objects.filter(username=username,inactive=False).exists():
                    return Response({'data': 'username_found'}, status=status.HTTP_200_OK)
                elif User.objects.filter(email=email,inactive=True).exists():
                    return Response({'data': 'inactive_user'},status=status.HTTP_200_OK)
            otp = generate_otp()
            if otp_record:
                    otp_record.otp = otp
                    otp_record.save()
                    data = { 'email': email, 'isfound': 'notfound'}
            else:
                    otp_data = {'email': email,'username':username,'password':password,'mobile':mobile, 'otp': otp}
                    otp_save = OTPSerializer(data=otp_data)
                    if otp_save.is_valid():
                        otp_save.save()
                        data = { 'email': email, 'isfound': 'notfound'}
                    else:
                        return Response(otp_save.errors, status=status.HTTP_400_BAD_REQUEST)
            if(type == 'send'):
                send_mail(
                    'Your One-Time Verification Code',
                    f"""
                    Dear {username},

                    Thank you for signing up with us!

                    To complete your registration and verify your account, please enter the following One-Time Password (OTP) on the verification page:

                    Your OTP is: {otp}

                    If you did not request this, please ignore this email.

                    Thank you for being a part of our community!  
                    If you have any questions, feel free to reach out to us at info@mi-bot.com.

                    Best regards,  
                    The MiBOT Ventures Team
                    """,
                    os.getenv('EMAIL_HOST_USER'),
                    [email],
                    fail_silently=False
                )
            elif(type == 'resend'):
                send_mail(
                    'Your Requested OTP - Resend',
                    f"""
                    Dear User,

                    As per your request, we are resending your One-Time Password (OTP).

                    Your OTP is: {otp}

                    If you did not request this, please ignore this email.

                    Thank you for being a valued user!  
                    If you have any questions, feel free to reach out to us at info@mi-bot.com.

                    Best regards,  
                    The MiBOT Ventures Team
                    """,
                    os.getenv('EMAIL_HOST_USER'),
                    [email],
                    fail_silently=False
                )

            return Response({'data': data, 'message': "OTP sent successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            email = request.query_params.get('email')
            code = request.query_params.get('code')
            otp = OTP.objects.filter(email=email).first()
            if otp is None:
                return Response({'error': 'OTP not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = OTPSerializer(otp)
            if serializer.data.get('otp') == code:
                otp.delete()  
                return Response({'data': 'matched'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'data': 'unmatched'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class Signup(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            code = request.data.get('code')
            forget = request.data.get('forget')
            otp = OTP.objects.filter(email=email,otp=code).first()
            if otp is None:
                return Response({'data': 'unmatched'}, status=status.HTTP_201_CREATED)
                # return Response({'error': 'OTP not found'}, status=status.HTTP_404_NOT_FOUND)
            elif forget:
                otp.delete() 
                return Response({'data': 'matched'}, status=status.HTTP_201_CREATED) 
            else:
                data = {'email':otp.email,'mobile':otp.mobile,'password':otp.password,'username':otp.username}
                if OfflinePurchase.objects.filter(customer_email=email).exists() or OfflinePurchase.objects.filter(customer_contact_number=otp.mobile).exists():
                    data['subscription'] = True
                else:
                    data['subscription'] = False
                serializer = UserSerializer(data=data,partial=True)
                if serializer.is_valid():
                    raw_password = serializer.validated_data.get('password')
                    encrypted_password = encrypt_password(raw_password)
                    serializer.save(password=encrypted_password)
                    otp.delete()
                    return Response({'data': 'matched'}, status=status.HTTP_201_CREATED)
                else:
                    print(serializer.errors)
                    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                  
        except Exception as e:
            print(f"Error: {str(e)}") 
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Forget(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            if User.objects.filter(email=email,inactive=False).exists():
                otp = generate_otp()
                otp_record = OTP.objects.filter(email=email).first()
                if otp_record:
                        otp_record.otp = otp
                        otp_record.save()
                else:
                    otp_data = {'email': email, 'otp': otp}
                    otp_save = OTPSerializer(data=otp_data,partial=True)
                    if otp_save.is_valid():
                        otp_save.save()
                    else:
                        return Response(otp_save.errors, status=status.HTTP_400_BAD_REQUEST)

                send_mail(
                    'Reset Your Password',
                    f"""
                    Dear User,

                    We received a request to reset your password.

                    To reset your password, please use the following One-Time Password (OTP) on the reset page:

                    Your OTP is: {otp}

                    If you did not request a password reset, please ignore this email and your password will remain unchanged.

                    Thank you for using our services!  
                    If you have any questions, feel free to reach out to us at info@mi-bot.com.

                    Best regards,  
                    The MiBOT Ventures Team
                    """,
                    os.getenv('EMAIL_HOST_USER'),
                    [email],
                    fail_silently=False
                )

                datas = {'email': email, 'isexists': 'yes'}
                return Response({'data': datas, 'message': "Mail sent successfully"}, status=status.HTTP_201_CREATED)
            else:
                data = {'email': email, 'isexists': 'no'}
                return Response({'data': data, 'message': "Unsuccessful, try again"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class UserReviews(APIView):
    def post(self, request):
        try:
            data = request.data
            if 'course' not in data or not data['course']:
                return Response({'error': 'Course ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            course = Course.objects.filter(id=data['course']).first()
            if not course:
                return Response({'error': 'Invalid course ID.'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserReviewSerializer(data=data)
            if serializer.is_valid():
                review_data = serializer.save()
                review_data_list = UserReview.objects.filter(course=review_data.course)
                reviews_list = []
                rating_sum = 0

                for review in review_data_list:
                    reviewer = User.objects.get(id=review.user.id)
                    reviews_list.append({
                        'id':review.id,
                        'username': reviewer.username,
                        'rating': review.rating,
                        'review': review.review,
                        'createdAt': review.created_at
                    })
                    rating_sum += review.rating
                
                rating_avg = rating_sum / len(reviews_list)
                course.rating = rating_avg
                course.save()
                
                return Response({'data': reviews_list}, status=status.HTTP_200_OK)
            else:
                print("Serializer errors:", serializer.errors)  
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            course_id = request.query_params.get('id')
        
            if not course_id:
                return Response({'error': 'Course ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            review_data = UserReview.objects.filter(course=course_id)
            reviews_list = []

            for review in review_data:
                reviews_list.append({
                    'id':review.id,
                    'username': review.user.username,  
                    'rating': review.rating,
                    'review': review.review,
                    'createdAt': review.created_at
                })

            return Response({'data': reviews_list}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class delcoursereview(APIView):
    def delete(self, request, id):
        try:
            reviewdel = UserReview.objects.get(id=id) 
            reviewdel.delete()
            return Response({"data": 'success','message': 'deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
class OrderAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')
            amount = data.get('amount')
            currency = data.get('currency')
            receipt = data.get('receipt')
            response = client.order.create(data={'amount': amount, 'currency': currency, 'receipt': receipt})
            response['user_id'] = user_id
            print(response)
            return Response({'data': response}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e)) 
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# hi gibs
class CheckoutAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')
            # amount = data.get('amount')
            # currency = data.get('currency')
            # receipt = data.get('receipt')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')
            print(data)
            # serializedTransaction = TransactionCheckOutSerializer(data=data)
            # if(serializedTransaction.is_valid()):
            response = client.utility.verify_payment_signature({'razorpay_order_id': razorpay_order_id,'razorpay_payment_id': razorpay_payment_id, 'razorpay_signature': razorpay_signature})
            serializedTransaction = TransactionCheckOutSerializer(data=data)
            if serializedTransaction.is_valid():
                # Save the serialized data
                serializedTransaction.save()
                usersub = User.objects.filter(id=user_id).first()
                usersub.subscription = True
                usersub.role = 'CourseSubscribedUser'
                usersub.save()
                print(serializedTransaction.data)
                return Response({'data': serializedTransaction.data}, status=status.HTTP_200_OK)
            else:
                print(serializedTransaction.errors)
                return Response({'error': serializedTransaction.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception:", str(e)) 
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class Advertisement(APIView):
    def get(self, request):
        try:
            data = AdvertisementBanner.objects.all()
            Ad = Adserial(data, many=True)
            return Response({'data': Ad.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        try:
            data = request.data
            serializer = Adserial(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'data': 'success'}, status=status.HTTP_200_OK)
            else:
                print(serializer.errors)
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception:", str(e))  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class Certify(APIView):
    def get(self, request):
        try:
            # Get the user ID from query parameters
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch user details
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Construct the full name
            full_name = f"{user.first_name or ''} {user.middle_name or ''} {user.last_name or ''}".strip()

            # Fetch certifications and related course details
            certification_data = UserCertificationScore.objects.filter(user_id=user_id).select_related('course')
            certify_list = []
            for certify in certification_data:
                if certify.total_marks > 0:  # Avoid division by zero
                    percentage = (certify.obtained_marks / certify.total_marks) * 100
                    if percentage >= 65:
                        certify_list.append({
                            'course_name': certify.course.course_name,  # Using select_related for optimization
                        })

            # Prepare response data
            data = {
                'certificates': certify_list,
                'user_name': full_name
            }
            return Response({'data': data}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log and return the error
            print("Exception:", str(e))
            return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActivityUploads(APIView):
    def post(self,request):
        try:
            data = request.data
            user = data.get('user')
            course = data.get('course')
            module = data.get('module')
            files = self.request.FILES 
            useruploads = files.get('userupload')
            isuserfound = ActivityFile.objects.filter(user=user,course=course,module=module).first()
            if not isuserfound:
                userupload = default_storage.save(useruploads.name, useruploads)  
                activity = ActivityFile.objects.create(
                    user=user,
                    course=course,
                    userupload=userupload,
                    module=module
                )
                serializer = ActivitiesSerializers(activity)
            else:
                filedata = isuserfound.userupload
                default_storage.delete(filedata)
                useruploading = default_storage.save(useruploads.name, useruploads)  
                isuserfound.userupload = useruploading
                isuserfound.save()
            return Response({'data': 'successfully uploaded'}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Checkstocks(APIView):
    def post(self,request):
        try:
            user = request.data.get('user')
            cart_items = CartData.objects.filter(user=user, transact=None)
            for productid in cart_items:
                productstock = Product.objects.filter(id=productid.product.id).first()
                if(productstock.stocks < productid.quantity):
                    return Response({'data': 'no stock'}, status=status.HTTP_200_OK)
            return Response({'data': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)