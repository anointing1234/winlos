from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_password_reset_email(email, code):
    subject = "Winlos Academy – Password Reset Code"

    message = f"""
Hello,

You requested to reset your password.

Your recovery code is:
{code}

This code expires in 20 minutes.

If you didn’t request this, please ignore this email.

— Winlos Academy
"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Password reset email failed for {email}: {e}")
        raise
