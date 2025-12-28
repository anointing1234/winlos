import os
import uuid
import random
from datetime import datetime
from io import BytesIO
from PIL import Image

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import pdfkit
from django.template.loader import render_to_string
import base64
from django.conf import settings
import re
from django.db.models import Sum




# =========================================
#   FILE UPLOAD PATH
# =========================================
def user_profile_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"profile_{uuid.uuid4()}.{ext}"
    return os.path.join("profile_pics", f"user_{instance.id}", filename)

# =========================================
#   ACCOUNT MANAGER
# =========================================
class AccountManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password or self.make_random_password())
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not password:
            raise ValueError("Superuser must have a password")
        return self.create_user(email, password, **extra_fields)

# =========================================
#   CHOICES
# =========================================
GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
)

ROLE = (
    ('student', 'Student'),
    ('instructor', 'Instructor'),
)

# =========================================
#   ACCOUNT MODEL
# =========================================
class Account(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True, max_length=100)
    username = models.CharField(max_length=30, unique=True, blank=True)
    fullname = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(
        max_length=15, blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    area_of_expertise = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    role = models.CharField(max_length=20, choices=ROLE, default='student')
    bio = models.CharField(max_length=300, blank=True)

    profile_pic = models.ImageField(upload_to=user_profile_upload_path, blank=True, null=True)

    # System
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(auto_now=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = AccountManager()

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    # =========================================
    #   USERNAME GENERATOR
    # =========================================
    def generate_username(self):
        import string
        if self.fullname:
            parts = self.fullname.strip().split()
            first_initial = parts[0][0].upper() if parts else random.choice(string.ascii_uppercase)
            last_initial = parts[-1][0].lower() if len(parts) > 1 else random.choice(string.ascii_lowercase)
        else:
            first_initial = random.choice(string.ascii_uppercase)
            last_initial = random.choice(string.ascii_lowercase)
        for _ in range(10):
            random_number = random.randint(100, 999)
            username = f"{first_initial}{last_initial}{random_number}@"
            if not Account.objects.filter(username=username).exists():
                self.username = username
                return username
        self.username = f"{first_initial}{last_initial}{int(datetime.now().timestamp())}@"
        return self.username

    # =========================================
    #   IMAGE COMPRESSION
    # =========================================
    def compress_image(self, image):
        img = Image.open(image)
        img = img.convert("RGB")
        img.thumbnail((600, 600))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        buffer.seek(0)
        return ContentFile(buffer.read(), name=image.name)

    @property
    def courses_count(self):
        return self.enrollments.filter(is_active=True).count()

    def profile_completion_percentage(self):
        """
        Calculates profile completeness based on filled fields.
        """
        fields_to_check = [
            'username', 'fullname', 'phone_number', 'country', 'city', 
             'gender', 'bio', 'profile_pic'
        ]

        filled_count = 0
        total_fields = len(fields_to_check)

        for field in fields_to_check:
            value = getattr(self, field)
            if value:
                filled_count += 1

        # Calculate percentage
        percentage = int((filled_count / total_fields) * 100)
        return percentage
    # =========================================
    #   SAVE OVERRIDE
    # =========================================
    def save(self, *args, **kwargs):
        if not self.username:
            self.generate_username()
        # Delete old profile picture if replaced
        if self.pk:
            try:
                old = Account.objects.get(pk=self.pk)
                if old.profile_pic and self.profile_pic != old.profile_pic:
                    old.profile_pic.delete(save=False)
            except Account.DoesNotExist:
                pass
        # Compress uploaded picture
        if self.profile_pic and hasattr(self.profile_pic, "file"):
            self.profile_pic = self.compress_image(self.profile_pic)
        super().save(*args, **kwargs)

    # =========================================
    #   DELETE USER — REMOVE IMAGE
    # =========================================
    def delete(self, *args, **kwargs):
        if self.profile_pic:
            self.profile_pic.delete(save=False)
        super().delete(*args, **kwargs)


# ================================================================
#                          ENROLLMENT
# ================================================================
class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("winlos_app.Account", on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.name_of_course}"



# ================================================================
#                          COURSE MODEL
# ================================================================
class Course(models.Model):

    COURSE_TYPES = [
        ("cinematography", "Cinematography"),
        ("scriptwriting", "Scriptwriting"),
        ("video_editing", "Video Editing"),
        ("sound_engineering", "Sound Engineering"),
        ("filmmaking", "Filmmaking"),
        ("set_design", "Set Design"),
        ("vfx_design", "VFX Design"),
        ("directing", "Directing"),
        ("acting", "Acting"),

        # Bundles
        ("indie_filmmaker_bundle", "Indie Filmmaker Bundle"),
        ("the_storyteller_bundle", "The Storyteller Bundle"),
        ("the_technical_bundle", "The Technical Bundle"),
        ("the_content_creation_bundle", "The Content Creation Bundle"),
        ("the_business_of_film_making_bundle", "The Business of Film Making Bundle"),
    ]





    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_type = models.CharField(max_length=50, choices=COURSE_TYPES)
    name_of_course = models.CharField(max_length=255)




    created_by = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="created_courses"
    )

    promotion_image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)

    purchased_users = models.ManyToManyField(
        Account,
        through="Enrollment",
        related_name="purchased_courses",
        blank=True
    )

    def __str__(self):
        return self.name_of_course

    # Optimize image AFTER save
    def optimize_image(self):
        if not self.promotion_image:
            return

        try:
            img = Image.open(self.promotion_image)
            img = img.convert("RGB")
            img = img.resize((500, 504), Image.LANCZOS)

            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)

            self.promotion_image.save(
                self.promotion_image.name,
                ContentFile(buffer.read()),
                save=False
            )

        except Exception as e:
            print("Image optimization failed:", e)

    # Delete old image correctly
    def delete_old_image(self):
        if not self.pk:
            return

        try:
            old = Course.objects.get(pk=self.pk)
        except Course.DoesNotExist:
            return

        if old.promotion_image and old.promotion_image != self.promotion_image:
            if os.path.isfile(old.promotion_image.path):
                os.remove(old.promotion_image.path)

    def save(self, *args, **kwargs):
        self.delete_old_image()
        super().save(*args, **kwargs)
        self.optimize_image()
        super().save(update_fields=['promotion_image'])

    @property
    def total_lessons(self):
        return self.lessons.count()
    
    @property
    def total_duration_minutes(self):
        return self.lessons.aggregate(
            total=Sum("duration_minutes")
        )["total"] or 0

    @property
    def average_rating(self):
        return round(self.rating, 1)
    
    @property
    def students_count(self):
        """
        Returns number of students who have purchased / enrolled in this course
        """
        return self.enrollments.filter(is_active=True).count()
    


# ================================================================
#                          LESSON MODEL
# ================================================================
class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # <-- New description field
    video = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=1, editable=False)

    class Meta:
        ordering = ['order']  # default ordering by the order field

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set order for new lessons
            last_order = Lesson.objects.filter(course=self.course).aggregate(models.Max('order'))['order__max']
            self.order = (last_order or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (Order: {self.order})"
    


# ================================================================
#                   LESSON PROGRESS MODEL
# ================================================================
class LessonProgress(models.Model):

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    completed_at = models.DateTimeField(blank=True, null=True)
    watched_duration = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0) 
    order = models.PositiveIntegerField(default=0) 
    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.status})"

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

        CourseProgress.update_user_progress(self.user, self.lesson.course)



# ================================================================
#                   COURSE PROGRESS MODEL
# ================================================================
class CourseProgress(models.Model):

    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('favorite', 'Favorite'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="course_progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="progress")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='saved')
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.name_of_course} ({self.status})"

    @staticmethod
    def update_user_progress(user, course):
        total = course.lessons.count()
        if total == 0:
            return

        completed = LessonProgress.objects.filter(
            user=user,
            lesson__course=course,
            status='completed'
        ).count()

        percent = (completed / total) * 100

        progress, _ = CourseProgress.objects.get_or_create(
            user=user,
            course=course
        )

        progress.progress_percent = round(percent, 2)
        progress.status = 'completed' if percent == 100 else 'ongoing'
        progress.save()






# =========================================
#            COURSE PAYMENT MODEL
# =========================================
class CoursePayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="payments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='NGN')
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.name_of_course} ({self.status})"




# ================================================================
#                        EXAM MODEL
# ================================================================
class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exams")

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    duration_minutes = models.PositiveIntegerField(default=20)
    total_marks = models.PositiveIntegerField(default=100)
    pass_mark = models.PositiveIntegerField(default=50)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.course.name_of_course} - {self.title}"

    @property
    def questions_count(self):
        return self.questions.count()


# ================================================================
#                       EXAM QUESTIONS
# ================================================================
class ExamQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    
    question_text = models.TextField()
    mark = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Q: {self.question_text[:40]}..."


# ================================================================
#                       ANSWER OPTIONS
# ================================================================
class ExamOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name="options")

    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.option_text} ({'Correct' if self.is_correct else 'Incorrect'})"


# ================================================================
#                   EXAM ATTEMPT MODEL
# ================================================================
class ExamAttempt(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("submitted", "Submitted"),
        ("completed", "Completed"),  # Changed from passed/failed
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="exam_attempts")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="attempts")

    score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress")

    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(blank=True, null=True)

    # NEW: Store user-selected answers per question
    selected_answers = models.JSONField(default=dict, blank=True)  # {question_id: [option_ids]}

    class Meta:
        unique_together = ("user", "exam")  # One attempt per user per exam

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} ({self.status})"

    def calculate_score(self, selected_options):
        """
        Calculate the user's score based on selected options.
        `selected_options` should be a dict {question_id: [selected_option_ids as strings]}
        """
        score = 0
        for question in self.exam.questions.all():
            # Convert correct option UUIDs to strings
            correct_options = set(str(opt_id) for opt_id in question.options.filter(is_correct=True).values_list("id", flat=True))
            user_selected = set(selected_options.get(str(question.id), []))

            if user_selected == correct_options:
                score += question.mark  # Full marks if all correct options selected

        self.score = score
        self.status = "completed"
        self.submitted_at = timezone.now()
        self.selected_answers = selected_options
        self.save()


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="certificates")

    certificate_id = models.CharField(max_length=20, unique=True, editable=False)
    issued_at = models.DateTimeField(default=timezone.now)

    # REMOVE PDF FILE FIELD if you no longer need it
    # pdf_file = models.FileField(upload_to="certificates/generated/", null=True, blank=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificate {self.certificate_id}"

    # Auto-generate certificate ID only
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


# ================================================================
#                    AUTHENTICATION CODES MODEL
# ================================================================
class AuthCode(models.Model):
    CODE_TYPE_CHOICES = [
        ("email_verification", "Email Verification"),
        ("password_reset", "Password Reset"),
        ("two_factor", "Two-Factor Authentication"),  # Optional future use
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="auth_codes")
    code_type = models.CharField(max_length=30, choices=CODE_TYPE_CHOICES)
    code = models.CharField(max_length=10)  # Could be numeric or alphanumeric
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "code_type"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.code_type} - {self.code}"

    def save(self, *args, **kwargs):
        # Default expiration: 20 minutes from creation
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=20)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at
    





class CourseComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)  # 1-5 stars
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} on {self.course.name_of_course}"