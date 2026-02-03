from django.shortcuts import render, redirect
import uuid
import requests
from django.contrib import messages
from django.http import JsonResponse,HttpResponse
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import os
import json, requests
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login ,logout
from django.utils import timezone
from django.db.models import Avg
from .models import (
Course,
Enrollment,
CourseProgress,
LessonProgress,
Lesson,
Exam,
ExamAttempt,
Certificate,
Account, Course,
AuthCode,
ExamQuestion,
ExamOption,
CoursePayment,
CourseComment

)
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.templatetags.static import static
from django.db.models import Count, Q
from .utils.auth_codes import create_password_reset_code
from .utils.emails import send_password_reset_email
import hmac
import hashlib
from django.db import transaction
from django.conf import settings as Set
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.utils.timezone import now



User = get_user_model()


def home(request):
    return render(request,'home_pages/index.html')


def about_us(request):
    return render(request,'home_pages/about_us.html')


def admission(request):
    return render(request,'home_pages/Admission.html')


def program(request):
    return render(request,'home_pages/program.html')


def facilitators(request):
    return render(request,'home_pages/facilitators.html')

def contact(request):
    return render(request,'home_pages/contact.html')



# team pages
def team1(request):
    return render(request,'home_pages/teams/Rev_Ohis_Ojeikere.html')

def team2(request):
    return render(request,'home_pages/teams/Grace_Okonkwo.html')

def team3(request):
    return render(request,'home_pages/teams/David_Mensah.html')

def team4(request):
    return render(request,'home_pages/teams/Sarah_Thompson.html')

def team5(request):
    return render(request,'home_pages/teams/Michael_Okafor.html')

def team6(request):
    return render(request,'home_pages/teams/Chioma_Nwankwo.html')

def team7(request):
    return render(request,'home_pages/teams/Joseph_Andoh.html')

def team8(request):
    return render(request,'home_pages/teams/Rebecca_Asante.html')



def Storytelling(request):
    return render(request,'home_pages/courses/Storytelling.html')

def Screenwriting(request):
    return render(request,'home_pages/courses/Screenwriting.html')

def Cinematography(request):
    return render(request,'home_pages/courses/Cinematography.html')

def Advanced_Acting(request):
    return render(request,'home_pages/courses/Advanced_Acting.html')

def Film_Editing(request):
    return render(request,'home_pages/courses/Film_Editing.html')

def Film_Directing(request):
    return render(request,'home_pages/courses/Film_Directing.html')

def Sound_Design(request):
    return render(request,'home_pages/courses/Sound_Design.html')

def Lighting_Design(request):
    return render(request,'home_pages/courses/Lighting_Design.html')

def Advanced_Film(request):
    return render(request,'home_pages/courses/Advanced_Film.html')

def Short_Firm(request):
    return render(request,'home_pages/courses/Short_Firm.html')

# stundent _ authentication pages
def register(request):
    return render(request,'auth/signup.html')


def logout_view(request):
    """
    Logs out the user and redirects to the login page.
    """
    logout(request)
    return redirect('apply')


def Admin_logout(request):
    logout(request)
    return redirect('Admin_access')



# --------------------------
# STUDENT DASHBOARD
# --------------------------
@login_required
def student_dashboard(request):
    user = request.user

    # Prefetch related courses and lessons to avoid N+1 queries
    enrollments = Enrollment.objects.filter(
        user=user,
        is_active=True
    ).select_related("course").prefetch_related("course__lessons")

    course_ids = [e.course.id for e in enrollments]

    # Fetch all progress objects in bulk
    progresses = CourseProgress.objects.filter(user=user, course_id__in=course_ids)
    progresses_dict = {p.course_id: p for p in progresses}

    user_courses = []
    enrolled_courses_count = enrollments.count()
    active_courses_count = 0
    completed_courses_count = 0

    for enrollment in enrollments:
        course = enrollment.course

        # Lessons count (prefetched)
        lessons_count = course.lessons.count()

        # Progress
        progress_obj = progresses_dict.get(course.id)
        progress = progress_obj.progress_percent if progress_obj else 0

        # Active vs completed
        if progress >= 100:
            completed_courses_count += 1
        else:
            active_courses_count += 1

        # Map fields expected by template
        course.thumbnail = course.promotion_image
        course.title = course.name_of_course
        course.category = {"name": course.get_course_type_display()}
        course.lessons_count = lessons_count
        course.progress_percent = progress
        course.reviews_count = 0  # placeholder
        course.instructor = course.created_by

        user_courses.append(course)

    context = {
        "user_courses": user_courses,
        "enrolled_courses_count": enrolled_courses_count,
        "active_courses_count": active_courses_count,
        "completed_courses_count": completed_courses_count,
    }

    return render(request, "student_portal/student_dashbord.html", context)





def student_profile(request):
    user = request.user
    profile_completion = user.profile_completion_percentage()

    # Fetch active enrollments
    enrollments = Enrollment.objects.filter(user=user, is_active=True).select_related("course")

    course_ids = [e.course.id for e in enrollments]

    # Fetch progress objects in bulk
    progresses = CourseProgress.objects.filter(user=user, course_id__in=course_ids)
    progresses_dict = {p.course_id: p for p in progresses}

    enrolled_courses_count = enrollments.count()
    completed_courses_count = 0

    # Count completed courses based on progress
    for enrollment in enrollments:
        course = enrollment.course
        progress_obj = progresses_dict.get(course.id)
        progress = progress_obj.progress_percent if progress_obj else 0

        if progress >= 100:
            completed_courses_count += 1

    # Certificates count
    certificates_count = Certificate.objects.filter(user=user).count()

    context = {
        "enrolled_courses_count": enrolled_courses_count,
        "completed_courses_count": completed_courses_count,
        "certificates_count": certificates_count,
        "profile_completion":  profile_completion,
    }

    return render(request, 'student_portal/student_profile.html', context)






    

def Settings(request):
    return render(request,'student_portal/student_profile_settings.html')



def ajax_signup(request):
    print("➡️ ajax_signup called")

    try:
        if request.method != "POST":
            print("❌ Not POST request")
            return JsonResponse({"status": "error", "message": "Invalid request method."})

        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        print("📝 DATA:", fullname, email)

        if not fullname or not email or not password:
            print("❌ Missing fields")
            return JsonResponse({"status": "error", "message": "All fields are required."})

        if User.objects.filter(email=email).exists():
            print("❌ Email already exists")
            return JsonResponse({"status": "error", "message": "Email already registered!"})

        print("✅ Creating user...")
        user = User.objects.create_user(
            fullname=fullname,
            email=email,
            password=password
        )

        print("✅ User created:", user.id)

        print("🔐 Logging user in...")
        auth_login(
            request,
            user,
            backend="winlos_app.backends.EmailBackend"
        )

        print("✅ Login success")

        return JsonResponse({
            "status": "success",
            "message": "Account created successfully!",
            "redirect_url": "/program/"
        })

    except Exception as e:
        print("🔥 SIGNUP ERROR:", repr(e))
        return JsonResponse({
            "status": "error",
            "message": "Internal signup error."
        })


def ajax_signin(request):
    print("➡️ ajax_signin called")

    try:
        if request.method != "POST":
            print("❌ Not POST request")
            return JsonResponse({"status": "error", "message": "Invalid request method."})

        email = request.POST.get("email")
        password = request.POST.get("password")

        print("📨 EMAIL:", email)
        print("🔑 PASSWORD PROVIDED:", bool(password))

        print("🔍 Authenticating...")
        user = authenticate(request, email=email, password=password)

        print("👤 Auth result:", user)

        if user is None:
            print("❌ Authentication failed")
            return JsonResponse({"status": "error", "message": "Invalid email or password."})

        print("✅ User authenticated, ID:", user.id)

        if not user.is_active:
            print("❌ User inactive")
            return JsonResponse({"status": "error", "message": "Your account is inactive."})

        if hasattr(user, "role"):
            print("🎭 User role:", user.role)
            if user.role != "student":
                print("❌ Role denied")
                return JsonResponse({
                    "status": "error",
                    "message": "Access denied. Only students can log in here."
                })
        else:
            print("⚠️ User has NO role attribute")

        print("🔐 Logging in user...")
        auth_login(
            request,
            user,
            backend="winlos_app.backends.EmailBackend"
        )

        print("✅ Login success")

        return JsonResponse({
            "status": "success",
            "message": "Login successful!",
            "redirect_url": "/program/"
        })

    except Exception as e:
        print("🔥 SIGNIN ERROR:", repr(e))
        return JsonResponse({
            "status": "error",
            "message": "Internal login error."
        })


def Courses(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request,'student_portal/student_courses.html',{"courses": courses})

def certification(request):
    user = request.user

    # Get all certificates for the current user
    certificates = Certificate.objects.filter(user=user).select_related('course', 'user').order_by('-issued_at')

    # Total Certificates
    total_certificates = certificates.count()

    # Courses Completed
    completed_courses_count = CourseProgress.objects.filter(user=user, status='completed').count()

    # Average Grade from completed exams
    avg_grade = ExamAttempt.objects.filter(user=user, status='completed').aggregate(
        avg_score=Avg('score')
    )['avg_score'] or 0

    context = {
        "certificates": certificates,
        "enrolled_courses_count": total_certificates,  # Total Certificates
        "active_courses_count": completed_courses_count,  # Courses Completed
        "completed_courses_count": round(avg_grade, 2),  # Average Grade
    }

    return render(request, 'student_portal/certification.html', context)

@login_required  # Needed for AJAX POST
def update_password(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            old_password = data.get("old_password")
            new_password = data.get("new_password")
            confirm_password = data.get("confirm_password")

            user = request.user

            # Check old password
            if not user.check_password(old_password):
                return JsonResponse({"success": False, "message": "Old password is incorrect."})

            # Ensure new password is not the same as old password
            if old_password == new_password:
                return JsonResponse({"success": False, "message": "New password cannot be the same as old password."})

            # Confirm new password match
            if new_password != confirm_password:
                return JsonResponse({"success": False, "message": "Passwords do not match."})

            # Password complexity validation
            strongPassword = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$")
            if not strongPassword.match(new_password):
                return JsonResponse({"success": False, "message": "New password does not meet all requirements."})

            # Update password
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep user logged in

            return JsonResponse({"success": True, "message": "Password updated successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method."})




def update_profile(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    user = request.user

    # Get data from FormData
    fullname     = request.POST.get('fullname', '').strip()
    username     = request.POST.get('username', '').strip()
    email        = request.POST.get('email', '').strip()
    phone_number = request.POST.get('phone_number', '').strip()
    country      = request.POST.get('country', '').strip()
    city         = request.POST.get('city', '').strip()
    bio          = request.POST.get('bio', '').strip()

    errors = {}

    # --- Validation ---
    if not fullname:
        errors['fullname'] = ["Full name is required."]

    if not username:
        errors['username'] = ["Username is required."]
    elif User.objects.exclude(pk=user.pk).filter(username__iexact=username).exists():
        errors['username'] = ["This username is already taken."]

    if not email:
        errors['email'] = ["Email is required."]
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors['email'] = ["Enter a valid email address."]
    elif User.objects.exclude(pk=user.pk).filter(email__iexact=email).exists():
        errors['email'] = ["This email is already registered."]

    # Return errors if any
    if errors:
        return JsonResponse({
            "success": False,
            "message": "Please fix the errors.",
            "errors": errors
        }, status=400)

    try:
        # --- Update user fields ---
        user.fullname = fullname
        user.username = username
        user.email = email

        # Optional fields
        if hasattr(user, 'phone_number'):
            user.phone_number = phone_number or None
        if hasattr(user, 'country'):
            user.country = country or None
        if hasattr(user, 'city'):
            user.city = city or None
        if hasattr(user, 'bio'):
            user.bio = bio or ""

        user.save()

        return JsonResponse({
            "success": True,
            "message": "Profile updated successfully!"
        })

    except Exception as e:
        # Debugging (remove in production)
        print("Update profile error:", e)
        return JsonResponse({
            "success": False,
            "message": "Something went wrong. Please try again."
        }, status=500)



def update_profile_picture(request):
    if 'imageUpload' not in request.FILES:
        return JsonResponse({
            "success": False,
            "message": "No image selected."
        }, status=400)

    file = request.FILES['imageUpload']

    # Validate file type
    valid_extensions = ['.jpg', '.jpeg', '.png']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        return JsonResponse({
            "success": False,
            "message": "Only JPG, JPEG, and PNG files are allowed."
        }, status=400)

    # Limit size (5MB)
    if file.size > 5 * 1024 * 1024:
        return JsonResponse({
            "success": False,
            "message": "Image too large. Max 5MB."
        }, status=400)

    try:
        # Delete old picture if exists (works for R2 / remote storage)
        if request.user.profile_pic:
            request.user.profile_pic.delete(save=False)

        # Save new picture
        request.user.profile_pic = file
        request.user.save()

        return JsonResponse({
            "success": True,
            "message": "Profile picture updated!",
            "image_url": request.user.profile_pic.url
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Will print full error for debugging
        return JsonResponse({
            "success": False,
            "message": "Failed to upload image."
        }, status=500)



def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    comments = course.comments.select_related('user').all()  # ensure related_name='comments' in model

    return render(request, "student_portal/course_detail.html", {
        "course": course,
        "comments":  comments,
    })

from django.db.models import Q




# --------------------------
# COURSE LIVE VIEW
# --------------------------
@login_required
def course_live(request, cour_id):
    course = get_object_or_404(Course.objects.prefetch_related('lessons'), id=cour_id)
    all_lessons = course.lessons.all().order_by('order')

    lesson_id = request.GET.get("lesson")
    lesson = None

    if lesson_id:
        lesson = next((l for l in all_lessons if str(l.id) == lesson_id), None)
    lesson = lesson or all_lessons.first()

    previous_lesson = next((l for l in reversed(all_lessons) if l.order < lesson.order), None) if lesson else None
    next_lesson = next((l for l in all_lessons if l.order > lesson.order), None) if lesson else None

    completed_lessons = 0
    lesson_completed = False
    exam = None
    exam_action = None

    if request.user.is_authenticated:
        # Bulk fetch lesson progress for this course
        lesson_progress_qs = LessonProgress.objects.filter(user=request.user, lesson__course=course)
        completed_lessons = lesson_progress_qs.filter(status='completed').count()

        if lesson:
            lp = next((lp for lp in lesson_progress_qs if lp.lesson_id == lesson.id), None)
            lesson_completed = bool(lp and lp.status == 'completed')

        # Exam and attempt
        exam = Exam.objects.filter(course=course).first()
        if exam:
            attempt = ExamAttempt.objects.filter(user=request.user, exam=exam).first()
            if attempt:
                exam_action = {
                    "in_progress": "continue",
                    "submitted": "review",
                    "completed": "results",
                }.get(attempt.status)
            else:
                exam_action = "start"

    total_lessons = all_lessons.count()
    progress = int((completed_lessons / total_lessons) * 100) if total_lessons else 0

    next_lesson_url = reverse('course_live', args=[str(course.id)]) + f'?lesson={next_lesson.id}' if next_lesson else None

    return render(request, 'student_portal/live_course.html', {
        'course': course,
        'lesson': lesson,
        'all_lessons': all_lessons,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'progress': progress,
        'exam': exam,
        'exam_action': exam_action,
        'lesson_completed': lesson_completed,
        'next_lesson_url': next_lesson_url,
    })


@login_required
def mark_lesson_complete(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required."}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    lesson_id = data.get("lesson_id")
    watched_seconds = data.get("watched_seconds", 0)
    if not lesson_id:
        return JsonResponse({"success": False, "error": "lesson_id required."}, status=400)

    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    # Get or create lesson progress
    lp, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'status': 'in_progress'}
    )

    # Check if lesson was already completed
    already_completed = lp.status == 'completed'

    # Only update if not completed
    if not already_completed:
        if watched_seconds and isinstance(watched_seconds, int):
            lp.watched_duration = max(lp.watched_duration or 0, watched_seconds)

        lp.status = 'completed'
        lp.completed_at = timezone.now()
        lp.save()

        # Update overall course progress
        CourseProgress.update_user_progress(request.user, course)

    # Calculate progress
    lesson_progress_qs = LessonProgress.objects.filter(user=request.user, lesson__course=course)
    total = course.lessons.count()
    completed = lesson_progress_qs.filter(status='completed').count()
    percent = round((completed / total) * 100, 2) if total > 0 else 0.0

    # Determine next lesson
    next_lesson = Lesson.objects.filter(course=course, order__gt=lesson.order).order_by('order').first()
    next_lesson_url = (
        reverse('course_live', args=[str(course.id)]) + f'?lesson={next_lesson.id}' 
        if next_lesson else None
    )

    # Exam action
    exam_action = None
    exam = Exam.objects.filter(course=course).first()
    if exam:
        attempt = ExamAttempt.objects.filter(user=request.user, exam=exam).first()
        if attempt:
            exam_action = {
                "in_progress": "continue",
                "submitted": "review",
                "completed": "results"
            }.get(attempt.status, "start")
        else:
            exam_action = "start"

    # Create certificate if course completed
    if completed == total:
        Certificate.objects.get_or_create(user=request.user, course=course)

    return JsonResponse({
        "success": True,
        "already_completed": already_completed,  # ✅ New flag
        "next_lesson_url": next_lesson_url,
        "course_completed": (completed == total),
        "progress_percent": percent,
        "exam_action": exam_action,
        "lesson_id": str(lesson.id),
    })



# ---------------------- Optimized Exam Views ----------------------

@login_required
def take_exam(request, course_id, exam_id):
    course = get_object_or_404(Course, id=course_id)
    exam = get_object_or_404(Exam.objects.prefetch_related('questions__options'), id=exam_id, course=course)

    # Get or create exam attempt
    attempt, _ = ExamAttempt.objects.get_or_create(user=request.user, exam=exam)

    # Questions and prefetch options (single DB hit)
    questions = list(exam.questions.all())

    total_questions = len(questions)
    completed_questions = 0 if attempt.status == 'in_progress' else total_questions
    progress = int((completed_questions / total_questions) * 100) if total_questions else 0

    context = {
        'course': course,
        'exam': exam,
        'questions': questions,
        'current_question': questions[0] if questions else None,
        'completed_questions': completed_questions,
        'total_questions': total_questions,
        'progress': progress,
    }
    return render(request, 'student_portal/exam_pages/quiz.html', context)


@login_required
def submit_exam(request, course_id, exam_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    exam = get_object_or_404(Exam.objects.prefetch_related('questions__options'), id=exam_id, course__id=course_id)
    attempt, _ = ExamAttempt.objects.get_or_create(
        exam=exam,
        user=request.user,
        defaults={'started_at': timezone.now()}
    )

    if attempt.status == "completed":
        return JsonResponse({"error": "Exam already submitted."}, status=400)

    # Collect selected options efficiently
    selected_options = {}
    correct_options = {}
    for question in exam.questions.all():
        values = request.POST.getlist(f"answers_{question.id}")
        selected_options[str(question.id)] = [str(v) for v in values]

        correct_options[str(question.id)] = [str(opt.id) for opt in question.options.all() if opt.is_correct]

    # Calculate score
    attempt.calculate_score(selected_options)

    return JsonResponse({
        "score": attempt.score,
        "total": exam.total_marks,
        "correct_options": correct_options,
        "message": "Exam submitted successfully!"
    })


def exam_results(request, course_id, exam_id):
    """
    Handles exam submission and calculates score.
    """
    exam = get_object_or_404(
        Exam.objects.prefetch_related('questions__options'),
        id=exam_id,
        course__id=course_id
    )

    # Get or create the user's attempt
    attempt, _ = ExamAttempt.objects.get_or_create(exam=exam, user=request.user)

    if request.method == "POST":
        # Collect answers from POST data
        user_answers = {}
        for question in exam.questions.all():
            values = request.POST.getlist(f'answers_{question.id}')
            user_answers[str(question.id)] = [str(v) for v in values]

        # Calculate score and save attempt
        attempt.calculate_score(user_answers)

    # Prepare questions + options for template
    questions_data = []
    for question in exam.questions.all():
        options = list(question.options.all())
        correct_ids = {str(opt.id) for opt in options if opt.is_correct}

        # Ensure selected_answers is always a dict
        attempt_answers = getattr(attempt, 'selected_answers', {}) or {}
        selected_ids = set(str(opt_id) for opt_id in attempt_answers.get(str(question.id), []))

        options_data = [
            {
                "option": option,
                "is_correct": str(option.id) in correct_ids,
                "is_selected": str(option.id) in selected_ids
            } for option in options
        ]

        questions_data.append({
            "question": question,
            "options_data": options_data
        })

    context = {
        "exam": exam,
        "attempt": attempt,
        "questions_data": questions_data
    }
    return render(request, 'student_portal/exam_pages/quiz_answer.html', context)


# ==============================
# View Only Exam Results
# ==============================
@login_required
def view_exam_results(request, course_id, exam_id):
    """
    Display previously submitted exam attempt for review.
    """
    exam = get_object_or_404(
        Exam.objects.prefetch_related('questions__options'),
        id=exam_id,
        course__id=course_id
    )
    attempt = get_object_or_404(ExamAttempt, exam=exam, user=request.user)

    # Ensure selected_answers is always a dictionary
    attempt_answers = getattr(attempt, 'selected_answers', {}) or {}

    questions_data = []
    for question in exam.questions.all():
        options = list(question.options.all())
        correct_ids = {str(opt.id) for opt in options if opt.is_correct}
        
        # Get the selected answer IDs for this question
        question_answers = attempt_answers.get(str(question.id), [])
        selected_ids = set(str(answer_id) for answer_id in question_answers)

        options_data = [
            {
                "option": option,
                "is_correct": str(option.id) in correct_ids,
                "is_selected": str(option.id) in selected_ids
            } for option in options
        ]

        questions_data.append({
            "question": question,
            "options_data": options_data
        })

    context = {
        "exam": exam,
        "attempt": attempt,
        "questions_data": questions_data
    }
    return render(request, 'student_portal/exam_pages/quiz_answer.html', context)



def view_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Fetch certificate
    certificate = Certificate.objects.filter(
        user=request.user,
        course=course
    ).first()

    if not certificate:
        return redirect('course_live', course_id)

    # ---------- WATERMARK ----------
    watermark_text = course.name_of_course.upper()

 
    # ---------- CONTEXT (using proper static URLs) ----------
    context = {
        "academy_name": "The Winlos Academy",

        # These will resolve correctly in dev and prod
          "logo_url": request.build_absolute_uri(
        static("assets/img/preloader.png")
            ),
            "signature_url": request.build_absolute_uri(
                static("assets/img/signature.png")
            ),
        "watermark_text": watermark_text,

        "full_name": getattr(request.user, "fullname", request.user.username),
        "course_name": course.name_of_course,
        "course_description": course.description or "",

        "issued_at": certificate.issued_at.strftime("%B %d, %Y"),
        "issued_on": certificate.issued_at.strftime("%B %d, %Y"),
        "certificate_id": certificate.certificate_id,

        "signer_name": "Academy Director",
        "signer_title": "Course Administrator",

    }

    return render(request, "certificates/certificate_template.html", context)







# ---------------------------------------- Admin views

def Admin_portal(request):
    return render(request,'auth/admin_authentication.html')


def admin_dash(request):
    # Get all active students
    students = Account.objects.filter(role='student', is_active=True).annotate(
        total_courses=Count('enrollments', filter=Q(enrollments__is_active=True), distinct=True),
        completed_courses_count=Count(
            'course_progress',
            filter=Q(course_progress__status='completed'),
            distinct=True
        )
    ).order_by('-date_joined')

    # Total successful course payments
    total_payments = CoursePayment.objects.filter(status='success').aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id')
    )

    # Total courses
    total_courses = Course.objects.count()

    context = {
        'students': students,
        'total_students': students.count(),
        'total_course_payments_count': total_payments['total_count'] or 0,
        'total_course_payments_amount': total_payments['total_amount'] or 0,
        'total_courses': total_courses,
    }

    return render(request, 'admin_portal/index.html', context)



def admin_profile(request):
    return render(request,'admin_portal/admin_profile.html')



def Admin_courses(request):
    # Only show courses created by the currently logged-in user
    courses = Course.objects.filter(created_by=request.user).order_by('-created_at')
    

    context = {
        "courses": courses
    }
    return render(request, 'admin_portal/courses.html', context)


def create_course_page(request):
    return render(request,'admin_portal/create_course.html')




def create_course_api(request):
    try:
        # -------------------------------
        # Create course
        # -------------------------------
        course = Course.objects.create(
            name_of_course=request.POST.get('name_of_course'),
            course_type=request.POST.get('course_type'),
            description=request.POST.get('description', ''),
            price=request.POST.get('price', 0),
            created_by=request.user,
            promotion_image=request.FILES.get('promotion_image')
        )

        lessons = []

        # -------------------------------
        # Create lessons (with duration)
        # -------------------------------
        for key in request.FILES:
            if key.startswith('lessons') and key.endswith('[video]'):
                idx = key.split('[')[1].split(']')[0]

                title = request.POST.get(f'lessons[{idx}][title]')
                video = request.FILES.get(f'lessons[{idx}][video]')
                duration = request.POST.get(f'lessons[{idx}][duration]', 0)

                try:
                    duration = int(duration)
                except (ValueError, TypeError):
                    duration = 0

                if title and video:
                    lesson = Lesson.objects.create(
                        course=course,
                        title=title,
                        video=video,
                        duration_minutes=duration  # ✅ duration in minutes
                    )
                    lessons.append(lesson)

        # -------------------------------
        # Update course stats
        # -------------------------------
        course.number_of_lessons = len(lessons)

        # Optional: total course duration
        course.total_duration = sum(l.duration_minutes for l in lessons)  # ✅ use duration_minutes
        course.save()

        return JsonResponse({
            "success": True,
            "message": "Course created successfully!",
            "course_id": str(course.id)
        })

    except Exception as e:
        print(f"⚠️ Developer error: {e}")
        return JsonResponse({
            "success": False,
            "message": "Failed to create course",
            "error": str(e)
        })



def admin_course_details(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lessons.all() if hasattr(course, 'lessons') else []
    instructor = course.created_by

    # Check if user already purchased or enrolled
    already_purchased = Enrollment.objects.filter(
        user=request.user, course=course
    ).exists()

    # Fetch all comments for this course
    comments = course.comments.select_related('user').all()  # select_related for user profile optimization

    context = {
        'course': course,
        'lessons': lessons,
        'instructor': instructor,
        'comments': comments,  # pass comments to template
        'already_purchased': already_purchased,
    }
    return render(request, 'admin_portal/admin_course_details.html', context)


def admin_delete_course(request, course_id):
    if request.method == "POST":
        course = get_object_or_404(Course, id=course_id)
        course_name = course.name_of_course
        course.delete()

        # Check if request is AJAX
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "status": "success",
                "message": f"Course '{course_name}' has been deleted successfully."
            })
        else:
            # fallback for normal POST requests
            messages.success(request, f"Course '{course_name}' has been deleted successfully.")
            return redirect('Admin_courses')
    
    # fallback for GET requests
    return redirect('Admin_courses')




# admin profile update 
def update_profile_details(request):
    if request.method == "POST":
        user = request.user
        try:
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.phone_number = request.POST.get("phone_number", user.phone_number)
            user.city = request.POST.get("city", user.city)
            user.country = request.POST.get("country", user.country)
            user.bio = request.POST.get("bio", user.bio)
            user.gender = request.POST.get("gender", user.gender)
            user.save()
            return JsonResponse({"success": True, "message": "Profile updated successfully!"})
        except Exception as e:
            print("Error updating profile:", e)
            return JsonResponse({"success": False, "message": "An error occurred while updating profile."})
    return JsonResponse({"success": False, "message": "Invalid request method."})




def update_cover_picture(request):
    """
    AJAX: Update user's cover picture (works with remote storage like Cloudflare R2)
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."})

    file = request.FILES.get("cover_pic")
    if not file:
        return JsonResponse({"success": False, "message": "No image uploaded."})

    user = request.user
    try:
        # Delete old cover picture if exists (remote storage safe)
        if user.cover_pic:
            user.cover_pic.delete(save=False)

        # Assign new file
        user.cover_pic = file
        user.save()

        # Build absolute URL
        cover_url = request.build_absolute_uri(user.cover_pic.url)

        return JsonResponse({
            "success": True,
            "message": "Cover photo updated successfully!",
            "cover_url": cover_url
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Optional: debug in console
        return JsonResponse({
            "success": False,
            "message": "Failed to update cover photo."
        })


def request_password_reset(request):
    email = request.POST.get("email", "").strip().lower()

    if not email:
        return JsonResponse({
            "status": "error",
            "message": "Email is required."
        })

    try:
        user = Account.objects.get(email=email, role="student", is_active=True)
    except Account.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "No student account found with this email."
        })

    code_obj = create_password_reset_code(user)
    send_password_reset_email(user.email, code_obj.code)

    return JsonResponse({
        "status": "success",
        "message": "Recovery code sent to your email."
    })






def confirm_password_reset(request):
    email = request.POST.get("email", "").strip().lower()
    code = request.POST.get("code", "").strip()
    new_password = request.POST.get("password", "")

    if not all([email, code, new_password]):
        return JsonResponse({
            "status": "error",
            "message": "All fields are required."
        })

    try:
        user = Account.objects.get(email=email, role="student", is_active=True)
    except Account.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Invalid request."
        })

    auth_code = AuthCode.objects.filter(
        user=user,
        code=code,
        code_type="password_reset",
        is_used=False
    ).first()

    if not auth_code:
        return JsonResponse({
            "status": "error",
            "message": "Invalid or used recovery code."
        })

    if auth_code.is_expired():
        return JsonResponse({
            "status": "error",
            "message": "Recovery code has expired."
        })

    user.password = make_password(new_password)
    user.save(update_fields=["password"])

    auth_code.is_used = True
    auth_code.save(update_fields=["is_used"])

    return JsonResponse({
        "status": "success",
        "message": "Password changed successfully."
    })







# -------------------------- 
# Instructor Signup (AJAX) - only for superusers
# --------------------------
def Admin_signup(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    # Only superusers can register new instructors
    if not request.user.is_superuser:
        return JsonResponse({"status": "error", "message": "Only admins can create instructor accounts."})

    fullname = request.POST.get("fullname")
    email = request.POST.get("email")
    password = request.POST.get("password")

    print("INSTRUCTOR SIGNUP ATTEMPT:", fullname, email)

    # Validation
    if not fullname or not email or not password:
        return JsonResponse({"status": "error", "message": "All fields are required."})

    if User.objects.filter(email=email).exists():
        return JsonResponse({"status": "error", "message": "Email already registered!"})

    # Create user with role = instructor
    user = User.objects.create_user(
        fullname=fullname,
        email=email,
        password=password,
        role="instructor"
    )

    # Automatically log in the new instructor
    auth_login(request, user)

    return JsonResponse({
        "status": "success",
        "message": "Instructor account created successfully!",
        "redirect_url": "/Admin_dashboard/"
    })


# --------------------------
# SIGNIN VIEW (AJAX) - only instructors & superusers
# --------------------------

def Admin_signin(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    email = request.POST.get("email")
    password = request.POST.get("password")

    print("LOGIN ATTEMPT:", email)

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"status": "error", "message": "Invalid email or password."})

    # Only allow superusers or instructors
    if not user.is_active:
        return JsonResponse({"status": "error", "message": "Your account is inactive."})
    if not (user.is_superuser or user.role == "instructor"):
        return JsonResponse({"status": "error", "message": "Access denied. Only instructors can log in."})

    auth_login(request, user)

    return JsonResponse({
        "status": "success",
        "message": "Login successful!",
        "redirect_url": "/Admin_dashboard/"
    })





# Admin reset password 


def Admin_password_reset(request):
    email = request.POST.get("email", "").strip().lower()

    if not email:
        return JsonResponse({
            "status": "error",
            "message": "Email is required."
        })

    try:
        user = Account.objects.get(email=email, role="instructor", is_active=True)
    except Account.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "No instructor account found with this email."
        })

    code_obj = create_password_reset_code(user)
    send_password_reset_email(user.email, code_obj.code)

    return JsonResponse({
        "status": "success",
        "message": "Recovery code sent to your email."
    })






def Admin_confirm_password_reset(request):
    email = request.POST.get("email", "").strip().lower()
    code = request.POST.get("code", "").strip()
    new_password = request.POST.get("password", "")

    if not all([email, code, new_password]):
        return JsonResponse({
            "status": "error",
            "message": "All fields are required."
        })

    try:
        user = Account.objects.get(email=email, role="instructor", is_active=True)
    except Account.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Invalid request."
        })

    auth_code = AuthCode.objects.filter(
        user=user,
        code=code,
        code_type="password_reset",
        is_used=False
    ).first()

    if not auth_code:
        return JsonResponse({
            "status": "error",
            "message": "Invalid or used recovery code."
        })

    if auth_code.is_expired():
        return JsonResponse({
            "status": "error",
            "message": "Recovery code has expired."
        })

    user.password = make_password(new_password)
    user.save(update_fields=["password"])

    auth_code.is_used = True
    auth_code.save(update_fields=["is_used"])

    return JsonResponse({
        "status": "success",
        "message": "Password changed successfully."
    })



# update records 
def ajax_update_course(request, course_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    user = request.user
    course = get_object_or_404(Course, pk=course_id)

    # Only course creator or staff can edit
    if user != course.created_by and not user.is_staff:
        return JsonResponse({"status": "error", "message": "You are not authorized to edit this course."})

    try:
        # Basic Info
        course.name_of_course = request.POST.get("name_of_course", course.name_of_course)
        course.course_type = request.POST.get("course_type", course.course_type)
        course.description = request.POST.get("description", course.description)
        course.price = request.POST.get("price", course.price)

        # Promotion Image
        if "promotion_image" in request.FILES:
            course.promotion_image = request.FILES["promotion_image"]

        course.save()
        print(f"[DEV] Course {course.id} updated successfully")

        # Update existing lessons
        for lesson in course.lessons.all():
            title = request.POST.get(f"lesson_title_{lesson.id}")
            description = request.POST.get(f"lesson_description_{lesson.id}")
            duration = request.POST.get(f"lesson_duration_{lesson.id}")
            video = request.FILES.get(f"lesson_video_{lesson.id}")

            if title:
                lesson.title = title
            if description is not None:
                lesson.description = description
            if duration:
                lesson.duration_minutes = int(duration)
            if video:
                lesson.video = video
            lesson.save()
            print(f"[DEV] Lesson {lesson.id} updated")

        # Add new lessons
        for key in request.POST.keys():
            if key.startswith("new_lesson_title_"):
                index = key.split("new_lesson_title_")[1]
                title = request.POST.get(f"new_lesson_title_{index}")
                description = request.POST.get(f"new_lesson_description_{index}", "")
                duration = request.POST.get(f"new_lesson_duration_{index}", 0)
                video = request.FILES.get(f"new_lesson_video_{index}")

                new_lesson = Lesson.objects.create(
                    course=course,
                    title=title,
                    description=description,
                    duration_minutes=int(duration),
                    video=video
                )
                print(f"[DEV] New Lesson {new_lesson.id} created")

        return JsonResponse({"status": "success", "message": "Course updated successfully!"})

    except Exception as e:
        print(f"[DEV] Error updating course: {e}")
        return JsonResponse({"status": "error", "message": "Failed to update course. Check console for details."})





# ===================== Admin: Create Exam Page =====================
def create_exam_questions(request):
    courses = Course.objects.all().order_by('name_of_course')
    return render(request, 'admin_portal/exam_q.html', {'courses': courses})


# ===================== API: Create Exam =====================
 # Only use csrf_exempt if using JS fetch with FormData
def create_exam_api(request):
    if request.method == 'POST':
        try:
            # Get exam info
            title = request.POST.get('title')
            course_id = request.POST.get('course')
            description = request.POST.get('description', '')
            duration_minutes = int(request.POST.get('duration_minutes', 20))
            total_marks = int(request.POST.get('total_marks', 100))
            pass_mark = int(request.POST.get('pass_mark', 50))

            course = get_object_or_404(Course, pk=course_id)

            # Create Exam
            exam = Exam.objects.create(
                title=title,
                course=course,
                description=description,
                duration_minutes=duration_minutes,
                total_marks=total_marks,
                pass_mark=pass_mark
            )

            # Parse questions from FormData
            questions = {}
            for key in request.POST:
                if key.startswith('questions'):
                    # key example: questions[0][question_text]
                    parts = key.replace(']', '').split('[')
                    q_index = parts[1]
                    q_field = parts[2]

                    questions.setdefault(q_index, {})
                    questions[q_index][q_field] = request.POST[key]

            # Parse options
            options = {}
            for key in request.POST:
                if key.startswith('questions') and 'options' in key:
                    # key example: questions[0][options][1][option_text]
                    parts = key.replace(']', '').split('[')
                    q_index = parts[1]
                    opt_index = parts[3]
                    opt_field = parts[4]

                    options.setdefault(q_index, {})
                    options[q_index].setdefault(opt_index, {})
                    options[q_index][opt_index][opt_field] = request.POST[key]

            # Create questions & options
            for q_index, q_data in questions.items():
                question = ExamQuestion.objects.create(
                    exam=exam,
                    question_text=q_data.get('question_text', ''),
                    mark=1  # default, can add mark field later
                )

                q_options = options.get(q_index, {})
                for opt_index, opt_data in q_options.items():
                    ExamOption.objects.create(
                        question=question,
                        option_text=opt_data.get('option_text', ''),
                        is_correct=opt_data.get('is_correct') in ['true', 'True', True, 'on']
                    )

            return JsonResponse({'success': True, 'message': 'Exam created successfully.'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



# ===================== Admin: List of Exams =====================
def admin_exams_page(request):
    exams = Exam.objects.all().select_related('course').order_by('-created_at')
    return render(request, 'admin_portal/exams_list.html', {'exams': exams})



def update_exam(request, exam_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"})

    exam = get_object_or_404(Exam, id=exam_id)

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    duration = data.get("duration_minutes")
    total_marks = data.get("total_marks")
    pass_mark = data.get("pass_mark")

    if not title:
        return JsonResponse({"success": False, "message": "Exam title cannot be empty"})

    exam.title = title
    exam.description = description

    if duration is not None:
        try:
            exam.duration_minutes = int(duration)
        except (ValueError, TypeError):
            pass  # ignore invalid

    if total_marks is not None:
        try:
            exam.total_marks = int(total_marks)
        except (ValueError, TypeError):
            pass

    if pass_mark is not None:
        try:
            exam.pass_mark = int(pass_mark)
        except (ValueError, TypeError):
            pass

    exam.save()
    return JsonResponse({"success": True, "message": "Exam updated successfully"})


def update_question(request, question_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"})

    question = get_object_or_404(ExamQuestion, id=question_id)

    text = data.get("question_text", "").strip()
    mark = data.get("mark")

    if not text:
        return JsonResponse({"success": False, "message": "Question text cannot be empty"})

    question.question_text = text

    if mark is not None:
        try:
            question.mark = max(1, int(mark))  # at least 1
        except (ValueError, TypeError):
            pass

    question.save()
    return JsonResponse({"success": True, "message": "Question updated"})


def update_option(request, option_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"})

    option = get_object_or_404(ExamOption, id=option_id)

    text = data.get("option_text", "").strip()
    is_correct = data.get("is_correct", False)

    if not text:
        return JsonResponse({"success": False, "message": "Option text cannot be empty"})

    option.option_text = text
    option.is_correct = bool(is_correct)
    option.save()

    return JsonResponse({"success": True, "message": "Option updated"})


# ======================= DELETE VIEWS (consistent response) =======================

def delete_exam(request, exam_id):
    if request.method == "POST":
        exam = get_object_or_404(Exam, id=exam_id)
        exam.delete()
        return JsonResponse({"status": "success", "message": "Exam deleted"})
    return JsonResponse({"status": "error", "message": "Invalid request"})


def delete_question(request, question_id):
    if request.method == "POST":
        question = get_object_or_404(ExamQuestion, id=question_id)
        question.delete()
        return JsonResponse({"status": "success", "message": "Question deleted"})
    return JsonResponse({"status": "error", "message": "Invalid request"})


def delete_option(request, option_id):
    if request.method == "POST":
        option = get_object_or_404(ExamOption, id=option_id)
        option.delete()
        return JsonResponse({"status": "success", "message": "Option deleted"})
    return JsonResponse({"status": "error", "message": "Invalid request"})











@login_required
def Admin_update_profile_details(request):
    """
    AJAX: Update user profile details
    """
    if request.method == "POST":
        user = request.user
        try:
            # Combine first_name and last_name into fullname
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            if first_name or last_name:
                user.fullname = f"{first_name} {last_name}".strip()
            
            user.phone_number = request.POST.get('phone_number', user.phone_number)
            user.city = request.POST.get('city', user.city)
            user.country = request.POST.get('country', user.country)
            user.gender = request.POST.get('gender', user.gender)
            user.bio = request.POST.get('bio', user.bio)

            user.save()
            return JsonResponse({"success": True, "message": "Profile updated successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})



@login_required
def Admin_update_profile_picture(request):
    """
    AJAX: Update admin profile picture (compatible with Cloudflare R2 / remote storage)
    """
    if request.method == "POST":
        user = request.user
        try:
            file = request.FILES.get('profile_pic')
            if file:
                # Delete old profile pic if exists (remote-safe)
                if user.profile_pic:
                    user.profile_pic.delete(save=False)

                # Assign new file (compress_image runs automatically in save())
                user.profile_pic = file
                user.save()

                return JsonResponse({
                    "success": True,
                    "message": "Profile picture updated successfully.",
                    "profile_url": user.profile_pic.url
                })
            else:
                return JsonResponse({"success": False, "message": "No file uploaded."})
        except Exception as e:
            import traceback
            print(traceback.format_exc())  # Optional: debug in console
            return JsonResponse({"success": False, "message": "Failed to upload image."})
    
    return JsonResponse({"success": False, "message": "Invalid request"})



@login_required
def Admin_update_password(request):
    """
    AJAX: Update password
    """
    if request.method == "POST":
        user = request.user
        current = request.POST.get("current_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        if not user.check_password(current):
            return JsonResponse({"success": False, "message": "Current password is incorrect."})

        if new != confirm:
            return JsonResponse({"success": False, "message": "Passwords do not match."})

        if len(new) < 6:
            return JsonResponse({"success": False, "message": "Password must be at least 6 characters."})

        user.set_password(new)
        user.save()
        update_session_auth_hash(request, user)  # keep user logged in
        return JsonResponse({"success": True, "message": "Password updated successfully."})

    return JsonResponse({"success": False, "message": "Invalid request"})




# payment connections 
def initialize_course_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    # Prevent double purchase
    if Enrollment.objects.filter(user=user, course=course).exists():
        return JsonResponse({"error": "Already enrolled"}, status=400)

    reference = f"COURSE-{uuid.uuid4()}"

    payment = CoursePayment.objects.create(
        user=user,
        course=course,
        amount=course.price,
        reference=reference,
        status="pending"
    )

    headers = {
        "Authorization": f"Bearer {Set.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": user.email,
        "amount": int(course.price * 100),  # Paystack uses kobo
        "reference": reference,
        "currency": "NGN",
        "callback_url": request.build_absolute_uri("/payment/success/"),
        "metadata": {
            "course_id": str(course.id),
            "user_id": str(user.id),
        }
    }

    response = requests.post(
        f"{Set.PAYSTACK_BASE_URL}/transaction/initialize",
        headers=headers,
        json=payload,
        timeout=10
    )

    data = response.json()

    if not data.get("status"):
        payment.status = "failed"
        payment.save()
        return JsonResponse({"error": "Payment init failed"}, status=500)

    return JsonResponse({
        "authorization_url": data["data"]["authorization_url"]
    })



def paystack_webhook(request):
    paystack_signature = request.headers.get("x-paystack-signature")

    computed_signature = hmac.new(
        Set.PAYSTACK_SECRET_KEY.encode(),
        request.body,
        hashlib.sha512
    ).hexdigest()

    # Security check
    if paystack_signature != computed_signature:
        return HttpResponse(status=401)

    event = json.loads(request.body)

    if event.get("event") == "charge.success":
        data = event["data"]
        reference = data["reference"]

        try:
            with transaction.atomic():
                payment = CoursePayment.objects.select_for_update().get(
                    reference=reference
                )

                # Prevent duplicate processing
                if payment.status == "success":
                    return HttpResponse(status=200)

                # ✅ Update payment
                payment.status = "success"
                payment.paid_at = timezone.now()
                payment.save(update_fields=["status", "paid_at"])

                # ✅ Create enrollment
                enrollment, created = Enrollment.objects.get_or_create(
                    user=payment.user,
                    course=payment.course,
                    defaults={"is_active": True}
                )

                # ✅ Create course progress (SAVED)
                CourseProgress.objects.get_or_create(
                    user=payment.user,
                    course=payment.course,
                    defaults={
                        "status": "saved",
                        "progress_percent": 0.00
                    }
                )

        except CoursePayment.DoesNotExist:
            pass  # Ignore invalid references

    return HttpResponse(status=200)



def payment_success(request):
    reference = request.GET.get("reference")

    if not reference:
        return redirect("dashboard")

    headers = {
        "Authorization": f"Bearer {Set.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(
        f"{Set.PAYSTACK_BASE_URL}/transaction/verify/{reference}",
        headers=headers,
        timeout=10
    )

    res = response.json()

    if res.get("status") and res["data"]["status"] == "success":
        try:
            payment = CoursePayment.objects.get(reference=reference)

            if payment.status != "success":
                with transaction.atomic():
                    payment.status = "success"
                    payment.paid_at = timezone.now()
                    payment.save()

                    Enrollment.objects.get_or_create(
                        user=payment.user,
                        course=payment.course,
                        defaults={"is_active": True}
                    )

                    CourseProgress.objects.get_or_create(
                        user=payment.user,
                        course=payment.course,
                        defaults={
                            "status": "saved",
                            "progress_percent": 0.00
                        }
                    )
        except CoursePayment.DoesNotExist:
            pass

    return redirect("dashboard")





def revenue_chart_data(request):
    current_year = now().year

    # Initialize all months with 0 revenue
    monthly_revenue = {month: 0 for month in range(1, 13)}

    # Aggregate successful payments by month
    payments = (
        CoursePayment.objects
        .filter(status='success', paid_at__year=current_year)
        .annotate(month=ExtractMonth('paid_at'))
        .values('month')
        .annotate(total=Sum('amount'))
    )

    for item in payments:
        monthly_revenue[item['month']] = float(item['total'])

    return JsonResponse({
        "months": [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ],
        "revenue": list(monthly_revenue.values())
    })



def add_course_comment(request, course_id):
    if request.method == "POST":
        course = get_object_or_404(Course, id=course_id)
        text = request.POST.get("comment", "").strip()
        rating = request.POST.get("rating", 0)

        if not text:
            return JsonResponse({"status": "error", "message": "Comment cannot be empty."})

        try:
            rating = int(rating)
            if rating < 0 or rating > 5:
                rating = 0
        except:
            rating = 0

        comment = CourseComment.objects.create(
            course=course,
            user=request.user,
            text=text,
            rating=rating
        )

        # Update course average rating
        all_ratings = course.comments.all().values_list("rating", flat=True)
        ratings_list = [r for r in all_ratings if r > 0]
        if ratings_list:
            course.rating = round(sum(ratings_list)/len(ratings_list), 1)
            course.save(update_fields=['rating'])

        # Build comment HTML
        rating_stars = "★"*comment.rating + "☆"*(5-comment.rating) if comment.rating else ""
        comment_html = f"""
        <div class="d-flex gap-16 mb-24 border-bottom pb-16">
            <div>
                <img src="{comment.user.profile_pic.url if comment.user.profile_pic else '/static/student_d_assets/images/profile_pic.png'}" 
                     class="rounded-circle" width="48" height="48" alt="">
            </div>
            <div class="flex-grow-1">
                <h6 class="fw-semibold mb-4" style="font-size: 14px;">
                    {comment.user.username}
                    <span class="text-muted" style="font-size: 12px;">• Just now</span>
                </h6>
                <p class="text-neutral-700" style="font-size: 14px; line-height: 20px;">
                    {comment.text}
                </p>
                {f'<p class="text-warning" style="font-size: 12px;">{rating_stars}</p>' if rating_stars else ''}
            </div>
        </div>
        """
        return JsonResponse({"status": "success", "message": "Comment added!", "comment_html": comment_html})

    return JsonResponse({"status": "error", "message": "Invalid request."})





# winlos_app/views.py
from django.views.debug import technical_500_response
import sys

def custom_500_view(request):
    if not Set.DEBUG:
        # Show full traceback even with DEBUG=False
        return technical_500_response(request, *sys.exc_info())
