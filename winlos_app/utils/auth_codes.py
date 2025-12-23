import random
from datetime import timedelta
from django.utils import timezone
from winlos_app.models import AuthCode  # Adjust the import to your app

def generate_6_digit_code():
    """Generate a 6-digit numeric code as string."""
    return str(random.randint(100000, 999999))

def create_password_reset_code(user):
    """
    Generate a new password reset code for a user.
    Before creating a new code, mark any previous unused codes as used.
    """
    # Invalidate any previous unused codes for this user
    AuthCode.objects.filter(
        user=user,
        code_type="password_reset",
        is_used=False
    ).update(is_used=True)

    # Create a new code
    new_code = AuthCode.objects.create(
        user=user,
        code_type="password_reset",
        code=generate_6_digit_code(),
        expires_at=timezone.now() + timedelta(minutes=20)
    )

    return new_code
