from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Account, Enrollment, Course, Lesson, LessonProgress,
    CourseProgress, Exam, ExamQuestion, ExamOption,
    ExamAttempt, Certificate, AuthCode,CoursePayment,
    CourseComment
)

# ================================
# INLINE MODELS
# ================================

class LessonInline(TabularInline):
    model = Lesson
    extra = 0
    fields = ["title", "order", "duration_minutes"]
    ordering = ["order"]


class ExamQuestionInline(TabularInline):
    model = ExamQuestion
    extra = 0
    fields = ["question_text", "mark"]


class ExamOptionInline(TabularInline):
    model = ExamOption
    extra = 0
    fields = ["option_text", "is_correct"]


# ================================
# ACCOUNT ADMIN
# ================================
@admin.register(Account)
class AccountAdmin(ModelAdmin):
    list_display = ["email", "username", "fullname", "role", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "gender", "date_joined"]
    search_fields = ["email", "username", "fullname", "phone_number"]
    readonly_fields = ["date_joined", "last_login"]

    fieldsets = (
        ("Personal Info", {
            "fields": ("email", "username", "fullname", "phone_number", "profile_pic")
        }),
        ("Location", {
            "fields": ("country", "city")
        }),
        ("Details", {
            "fields": ("gender", "role", "area_of_expertise", "bio")
        }),
        ("System", {
            "fields": ("date_joined", "last_login", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
    )


# ================================
# COURSE ADMIN
# ================================
@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ["name_of_course", "course_type", "created_by", "price", "rating", "created_at"]
    list_filter = ["course_type", "created_at"]
    search_fields = ["name_of_course", "description"]
    inlines = [LessonInline]
    autocomplete_fields = ["created_by"]


# ================================
# ENROLLMENT ADMIN
# ================================
@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ["user", "course", "enrolled_at", "is_active"]
    list_filter = ["is_active", "enrolled_at"]
    search_fields = ["user__email", "course__name_of_course"]
    autocomplete_fields = ["user", "course"]


# ================================
# LESSON ADMIN
# ================================
@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = ["title", "course", "order", "duration_minutes"]
    list_filter = ["course"]
    search_fields = ["title", "course__name_of_course"]
    autocomplete_fields = ["course"]


# ================================
# LESSON PROGRESS ADMIN
# ================================
@admin.register(LessonProgress)
class LessonProgressAdmin(ModelAdmin):
    list_display = ["user", "lesson", "status", "watched_duration", "completed_at"]
    list_filter = ["status", "completed_at"]
    search_fields = ["user__email", "lesson__title"]
    autocomplete_fields = ["user", "lesson"]


# ================================
# COURSE PROGRESS ADMIN
# ================================
@admin.register(CourseProgress)
class CourseProgressAdmin(ModelAdmin):
    list_display = ["user", "course", "status", "progress_percent", "last_accessed"]
    list_filter = ["status"]
    search_fields = ["user__email", "course__name_of_course"]
    autocomplete_fields = ["user", "course"]


# ================================
# EXAM ADMIN
# ================================
@admin.register(Exam)
class ExamAdmin(ModelAdmin):
    list_display = ["course", "title", "duration_minutes", "total_marks", "pass_mark", "created_at"]
    search_fields = ["title", "course__name_of_course"]
    inlines = [ExamQuestionInline]
    autocomplete_fields = ["course"]


@admin.register(ExamQuestion)
class ExamQuestionAdmin(ModelAdmin):
    list_display = ["exam", "question_text", "mark"]
    search_fields = ["question_text", "exam__title"]
    inlines = [ExamOptionInline]
    autocomplete_fields = ["exam"]


@admin.register(ExamOption)
class ExamOptionAdmin(ModelAdmin):
    list_display = ["question", "option_text", "is_correct"]
    list_filter = ["is_correct"]
    search_fields = ["option_text"]
    autocomplete_fields = ["question"]


# ================================
# EXAM ATTEMPTS
# ================================
@admin.register(ExamAttempt)
class ExamAttemptAdmin(ModelAdmin):
    list_display = ["user", "exam", "score", "status", "started_at", "submitted_at"]
    list_filter = ["status"]
    search_fields = ["user__email", "exam__title"]
    autocomplete_fields = ["user", "exam"]



# ================================
# CERTIFICATES (UPDATED)
# ================================
@admin.register(Certificate)
class CertificateAdmin(ModelAdmin):
    list_display = ["certificate_id", "user", "course", "issued_at"]
    list_filter = ["issued_at", "course"]
    search_fields = [
        "certificate_id",
        "user__email",
        "user__username",
        "course__name_of_course"
    ]
    autocomplete_fields = ["user", "course"]


# ================================
# AUTH CODES
# ================================
@admin.register(AuthCode)
class AuthCodeAdmin(ModelAdmin):
    list_display = ["id", "code_type", "user", "created_at"]
    list_filter = ["code_type", "created_at"]
    search_fields = ["user__email"]
    autocomplete_fields = ["user"]





# ================================
# COURSE PAYMENT ADMIN
# ================================
@admin.register(CoursePayment)
class CoursePaymentAdmin(ModelAdmin):
    list_display = ["user", "course", "amount", "currency", "status", "reference", "paid_at", "created_at"]
    list_filter = ["status", "currency", "created_at", "paid_at"]
    search_fields = ["user__email", "user__username", "course__name_of_course", "reference"]
    autocomplete_fields = ["user", "course"]
    readonly_fields = ["created_at", "paid_at", "reference"]



@admin.register(CourseComment)
class CourseCommentAdmin(ModelAdmin):
    list_display = [
        "course",
        "user",
        "rating",
        "created_at",
    ]

    list_filter = [
        "rating",
        "created_at",
        "course",
    ]

    search_fields = [
        "course__name_of_course",
        "user__email",
        "user__username",
        "text",
    ]

    autocomplete_fields = [
        "course",
        "user",
    ]

    readonly_fields = [
        "created_at",
    ]

    fieldsets = (
        ("Comment Details", {
            "fields": ("course", "user", "rating")
        }),
        ("Content", {
            "fields": ("text",)
        }),
        ("System", {
            "fields": ("created_at",)
        }),
    )