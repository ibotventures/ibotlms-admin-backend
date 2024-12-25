from django.urls import path
from .views import (CourseListCreateAPIView, CourseDetailAPIView, SignUpAPIView, SignInAPIView, ModuleAPIView, 
                    ModuleDetailAPIView, OfflinePurchaseList, OfflinePurchaseDetail, ModuleFileAPIView,
                    AssessmentCreateAPIView, AssessmentDetailAPIView, CategoryAPIView, ProductAPIView, CourseUserVisibilityAPIView,
                    CertificationAPIView, CertificationQuestionAPIView)

urlpatterns = [
    path('courses/', CourseListCreateAPIView.as_view(), name='course-list-create'),
    path('courses/<uuid:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('user/signin/', SignInAPIView.as_view(), name='user_signin'),  
    path('user/', SignUpAPIView.as_view(), name='user_create'),  
    path('user/<uuid:pk>/', SignUpAPIView.as_view(), name='user_detail'), 
    path('modules/', ModuleAPIView.as_view(), name='create_module'),  # POST to create a new module
    path('modules/course/<uuid:course_id>/', ModuleAPIView.as_view(), name='list_modules_by_course'),  # GET to list modules by course ID
    path('modules/<uuid:module_id>/', ModuleAPIView.as_view(), name='update_module'),  # PUT to update a module by ID
    path('modules/delete/<uuid:module_id>/', ModuleAPIView.as_view(), name='delete_module'),  # DELETE to delete a module by ID
    path('modules/module/<uuid:module_id>/', ModuleDetailAPIView.as_view(), name='module_detail'),  # GET and PATCH
    path('offline-purchases/', OfflinePurchaseList.as_view(), name='offline-purchase-list'),
    path('offline-purchases/<uuid:id>/', OfflinePurchaseDetail.as_view(), name='offline-purchase-detail'),
    path('module/file/', ModuleFileAPIView.as_view(), name='module-file'),
    path('assessments/module/<str:module_id>/', AssessmentCreateAPIView.as_view(), name='assessment_by_module'),
    path('assessments/', AssessmentCreateAPIView.as_view(), name='create_assessment'),
    path('assessments/<str:pk>/', AssessmentDetailAPIView.as_view(), name='assessment_detail'),
    path('categories/', CategoryAPIView.as_view()),  # For GET and POST
    path('categories/<str:pk>/', CategoryAPIView.as_view()),  # For PUT and DELETE
    path('products/', ProductAPIView.as_view()),  # For GET and POST
    path('products/<str:pk>/', ProductAPIView.as_view()),  # For PUT and DELETE
    path('course-user-visibility/', CourseUserVisibilityAPIView.as_view(), name='course-user-visibility'),
    path('certification/', CertificationAPIView.as_view(), name='certification'),                # POST, GET by course_id
    path('certification/<uuid:id>/', CertificationAPIView.as_view()),
    path('certification-question/', CertificationQuestionAPIView.as_view()),                # POST, GET by certification_id
    path('certification-question/<uuid:id>/', CertificationQuestionAPIView.as_view()),
]