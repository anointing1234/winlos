from django.urls import path, re_path
from django.conf import settings
from . import views
from django.views.static import serve
from .decorators import student_required, admin_required  # import your decorators

urlpatterns = [

    # Main page URLs — public
    path('', views.home, name="home"),
    path('home/', views.home, name="home"),
    path('about_us/', views.about_us, name="about_us"),
    path('admission/', views.admission, name="admission"),
    path('program/', views.program, name='program'),

    # Student authentication — public
    path('apply/', views.register, name='apply'),
    path("signup/", views.ajax_signup, name="signup"),
    path("Login/", views.ajax_signin, name="Login"),
    path('logout/', views.logout_view, name='logout'),
    path('Admin_logout/', views.Admin_logout, name='Admin_logout'),
    path('update-password/', views.update_password, name='update_password'),

    # Student portal views — student only
    path('dashboard/', student_required(views.student_dashboard), name='dashboard'),
    path('student_profile/', student_required(views.student_profile), name='student_profile'),
    path('settings/', student_required(views.settings), name='settings'),
    path('courses/', student_required(views.Courses), name='courses'),
    path('certification/', student_required(views.certification), name='certification'),
    path('update_profile/', student_required(views.update_profile), name='update_profile'),
    path('update_profile_picture/', student_required(views.update_profile_picture), name='update_profile_picture'),
    path('course/<uuid:course_id>/', student_required(views.course_detail), name='course_detail'),
    path('course_live/<uuid:cour_id>/', student_required(views.course_live), name='course_live'),
    path('api/lesson/mark-complete/', student_required(views.mark_lesson_complete), name='mark_lesson_complete'),
   
    # Exams/Quiz — student only
    path('course/<uuid:course_id>/exam/<uuid:exam_id>/', student_required(views.take_exam), name='take_exam'),
    path('courses/<uuid:course_id>/exams/<uuid:exam_id>/submit/', student_required(views.submit_exam), name='submit_exam'),
    path('exam/<uuid:course_id>/<uuid:exam_id>/results/', student_required(views.exam_results), name='exam_results'),
    path('courses/<uuid:course_id>/exams/<uuid:exam_id>/results/', student_required(views.view_exam_results), name='view_exam_results'),
    path('certificate/<uuid:course_id>/', student_required(views.view_certificate), name='view_certificate'),

    # Payments — student only
    path("pay/course/<uuid:course_id>/", student_required(views.initialize_course_payment), name="pay_course"),
    path("pay/verify/", views.paystack_webhook, name="paystack_webhook"),  # webhook public
    path("payment/success/", student_required(views.payment_success), name="payment_success"),

    # Admin URLs — admin/instructor only
    path('Admin_dashboard/', admin_required(views.admin_dash), name='Admin_dashboard'),
    path('Admin_courses/', admin_required(views.Admin_courses), name='Admin_courses'),
    path('create_course_page/', admin_required(views.create_course_page), name='create_course_page'),
    path('create_course_api/', admin_required(views.create_course_api), name='create_course_api'),
    path('admin_course_details/<uuid:pk>/', admin_required(views.admin_course_details), name='admin_course_details'),
    path('courses/delete/<uuid:course_id>/', admin_required(views.admin_delete_course), name='admin_delete_course'),
    path('admin_profile/', admin_required(views.admin_profile), name='admin_profile'),
    path('update_cover-picture/', admin_required(views.update_cover_picture), name='update_cover_picture'),
    path('update_profile-picture/', admin_required(views.update_profile_picture), name='update_profile-picture'),
    path('update_profile_details/', admin_required(views.update_profile_details), name='update_profile_details'),

    # Admin/Instructor exams management
    path("ajax/course/update/<uuid:course_id>/", views.ajax_update_course, name='ajax_update_course'),
    path("create_exam_questions/", admin_required(views.create_exam_questions), name="create_exam_questions"),
    path('create_exam_api/', admin_required(views.create_exam_api), name='create_exam_api'),
    path('Admin_exams/', admin_required(views.admin_exams_page), name='Admin_exams'),
    path('update_exam/<uuid:exam_id>/', admin_required(views.update_exam), name='update_exam'),
    path('delete_exam/<uuid:exam_id>/', admin_required(views.delete_exam), name='delete_exam'),
    path('update_question/<uuid:question_id>/', admin_required(views.update_question), name='update_question'),
    path('delete_question/<uuid:question_id>/', admin_required(views.delete_question), name='delete_question'),
    path('update_option/<uuid:option_id>/', admin_required(views.update_option), name='update_option'),
    path('delete_option/<uuid:option_id>/', admin_required(views.delete_option), name='delete_option'),
    path('Admin_update_profile_details/', admin_required(views.Admin_update_profile_details), name='Admin_update_profile_details'),
    path('Admin_update_profile_picture/', admin_required(views.Admin_update_profile_picture), name='Admin_update_profile_picture'),
    path('Admin_update_password/', admin_required(views.Admin_update_password), name='Admin_update_password'),

    # Admin authentication — public
    path('Admin_access/',views.Admin_portal,name="Admin_access"),  # maybe student portal access
    path("Admin_signup/", views.Admin_signup, name="Admin_signup"),
    path("Admin_Login/", views.Admin_signin, name="Admin_Login"),
    path("Admin_password_reset/", views.Admin_password_reset, name="Admin_password_reset"),
    path("Admin_password_reset_confirm/", views.Admin_confirm_password_reset, name="Admin_password_reset_confirm"),
    path('revenue_chart_data/', views.revenue_chart_data, name='revenue_chart_data'),
    path('course/<uuid:course_id>/add_comment/', views.add_course_comment, name='add_course_comment'),

    # Reset password URLs — public
    path("auth/password-reset/", views.request_password_reset, name="password_reset"),
    path("auth/password-reset/confirm/", views.confirm_password_reset, name="password_reset_confirm"),
   
    # Media/Static serving (dev only)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
