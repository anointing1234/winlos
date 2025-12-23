from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles=None, login_url='login', unauthorized_url='dashboard'):
    """
    Restrict access to authenticated users with specific roles.
    - allowed_roles: list of roles allowed (e.g., ['student', 'instructor'])
    - login_url: redirect if user is not logged in
    - unauthorized_url: redirect if logged-in user not allowed
    """
    allowed_roles = allowed_roles or []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Not authenticated
            if not request.user.is_authenticated:
                return redirect(login_url)

            # Authenticated — check role or staff status
            user_role = getattr(request.user, 'role', None)
            user_is_staff = getattr(request.user, 'is_staff', False)

            # If user is staff, always allow
            if user_is_staff:
                return view_func(request, *args, **kwargs)

            # Check role
            if user_role not in allowed_roles:
                return redirect(unauthorized_url)

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator


# Specific decorators

def student_required(view_func):
    """Only students can access this view"""
    return role_required(
        allowed_roles=['student'],
        login_url='apply',           # redirect to student login
        unauthorized_url='dashboard' # redirect if logged in but not student
    )(view_func)


def instructor_required(view_func):
    """Only instructors (non-staff) can access this view"""
    return role_required(
        allowed_roles=['instructor'],
        login_url='Admin_access',     # redirect to admin login
        unauthorized_url='dashboard'
    )(view_func)


def admin_required(view_func):
    """Only staff/admins can access this view"""
    return role_required(
        allowed_roles=[],            # no specific role needed
        login_url='Admin_access',     # redirect if not logged in
        unauthorized_url='dashboard'
    )(view_func)
