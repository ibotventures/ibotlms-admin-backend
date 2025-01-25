from django.urls import path
from .views import (CourseListCreateAPIView, CourseDetailAPIView, SignUpAPIView, SignInAPIView, ModuleAPIView, 
                    ModuleDetailAPIView, OfflinePurchaseList, OfflinePurchaseDetail, ModuleFileAPIView,
                    AssessmentCreateAPIView, AssessmentDetailAPIView, CategoryAPIView, ProductAPIView, CourseUserVisibilityAPIView,
                    CertificationAPIView, CertificationQuestionAPIView, SignIn, Signup, SendOTP, Forget, UpdatePassword, getdetails, updatedetails, buyerct, transact, cartproduct, carttransact, delcart, getprodetail, activates, delcoursereview, delproductreview, SubscriptionAmount,
                    UploadCourse, UploadModule, AssessmentQuestion, delaccount, DeleteModuleView, deleteQuestion, deleteCourse, courseconfirm, addproduct,
                    OfflinePurchaseUserAPIView, deletecertifyques, StatisticsAPIView, canaccesscourse, tasktrack, canviewmodule, pickup, FetchCoursePreview,
                    courselist, checkanswers, checkcertifyanswer, CourseListView, ProductView, ProductReviews, Eachproduct, Userscheck, UserReviews, 
                    UserCourses, categories, OrderAPIView, CheckoutAPIView, CertificationUpdateAPIView,Advertisement,CertificationAPIViews,Certify)

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
    
    
    path('signin/', SignIn.as_view(), name='signin'),
    path('signup/',Signup.as_view(),name='signup'),
    path('sendotp/',SendOTP.as_view(),name='sendotp'),
    path('forget/',Forget.as_view(),name='forget'),
    path('updatepassword/',UpdatePassword.as_view(),name='updatepassword'),
    path('getdetail/',getdetails.as_view(),name='getdetail'),
    path('updatedetails/',updatedetails.as_view(),name='updatedetils'),

    path('uploadcourse/',UploadCourse.as_view(),name='uploadcourse'),
    path('uploadmodule/',UploadModule.as_view(),name='uploadmodule'),
    path('assessmentquestion/',AssessmentQuestion.as_view(),name='assessmentquestion'),
    path('deleteaccount/',delaccount.as_view(),name='deleteaccount'),
    path('deletemodule/<uuid:id>/', DeleteModuleView.as_view(), name='deletemodule'),
    path('deleteques/<uuid:id>/',deleteQuestion.as_view(),name='deleteques'),
    path('deletecourse/<uuid:id>/',deleteCourse.as_view(),name='deletecourse'),
    path('confirm/',courseconfirm.as_view(),name='confirm'),
    path('addproduct/',addproduct.as_view(),name='addproduct'),
    path('categories/', CategoryAPIView.as_view()),  # For GET and POST
    path('offlinepurchase/', OfflinePurchaseUserAPIView.as_view(), name='offlinepurchase'),
    path('deletecertifyques/<uuid:id>/<uuid:courseid>/',deletecertifyques.as_view(),name='deletecertifyques'),
    path('statistics/', StatisticsAPIView.as_view(), name='statistics'),

    path('canaccesscourse/',canaccesscourse.as_view(),name='canaccesscourse'),
    path('tasktracking/',tasktrack.as_view(),name='tasktrack'),
    path('canviewmodule/',canviewmodule.as_view(),name='canviewmodule'),
    path('pickup/',pickup.as_view(),name='pickup'),
    path('coursepreview/',FetchCoursePreview.as_view(),name='course-preview'),
    path('courselist/',courselist.as_view(),name='courselist'),
    path('submitanswers/',checkanswers.as_view(),name='submitanswers'),
    path('submitcertificationanswers/',checkcertifyanswer.as_view(),name='submitcertificationanswer'),
    path('coursescategory/', CourseListView.as_view(), name='course-list'),
    path('productfilter/',ProductView.as_view(),name='productfilter'),
    path('productreviews/',ProductReviews.as_view(),name='productreviews'),
    path('eachproduct/', Eachproduct.as_view(),name='eachproduct'),
    path('isallowed/',Userscheck.as_view(),name='isallowed'),
    path('reviews/',UserReviews.as_view(),name='reviews'),
    path('userstartedcourses/',UserCourses.as_view(),name='usercourses'),
    path('listcategory/',categories.as_view(),name='listcategory'),
    
    path('order/', OrderAPIView.as_view(), name='order'),    
    path('orderStatus/', CheckoutAPIView.as_view(), name='checkout'),
   
    path('certifications/', CertificationAPIViews.as_view(), name='certifications'),
    path('certificationsupdate/<uuid:pk>/', CertificationUpdateAPIView.as_view(), name='certification-detail'),  
    
    path('buyercount/', buyerct.as_view(),name='buyercount'),
    path('transact/', transact.as_view(), name='transact'),
    path('productcart/', cartproduct.as_view(), name='productcart'),
    path('usercart/',carttransact.as_view(),name='usercart'),
    path('delcart/<uuid:id>/',delcart.as_view(),name='delcart'),
    path('getprodetail/',getprodetail.as_view(),name='getprodetail'),
    path('activateaccount/',activates.as_view(),name='activateaccount'),
    path('delcoursereview/<uuid:id>/',delcoursereview.as_view(),name='delcoursereview'),
    path('delproductreview/<uuid:id>/',delproductreview.as_view(),name='delproductreview'),
    path('getsubscription/', SubscriptionAmount.as_view(), name='getsubscription'),
    path('advertise/',Advertisement.as_view(),name='advertise'), 
    path('issuecertificate/',Certify.as_view(),name='issuecertificate'),
    
]