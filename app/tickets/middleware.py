from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request - check if profile is completed
        if request.user.is_authenticated:
            # Skip check for admin pages
            if request.path.startswith('/admin/'):
                return self.get_response(request)
                
            # Skip the check for logout URL
            if request.path == reverse('logout'):
                return self.get_response(request)
                
            # Skip the check for profile URL itself
            if request.path == reverse('profile'):
                return self.get_response(request)
                
            # Skip for static files
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                return self.get_response(request)
            
            # Check if user has a profile and if it's complete
            try:
                if not request.user.user_meta.is_profile_completed:
                    messages.warning(request, 'Please complete your profile before accessing other pages.')
                    return redirect('profile')
            except:
                # If user_meta doesn't exist, proceed normally 
                # (it will be created in the profile view)
                pass
                
        response = self.get_response(request)
        return response


class RoleBasedAccessMiddleware:
    """Middleware to enforce role-based access control:
    - Customers can only access customer-facing pages
    - Support agents and admins can ONLY use the admin interface
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request before it reaches the view
        if request.user.is_authenticated:
            # Skip for static files and media
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                return self.get_response(request)
                
            # Check user role
            try:
                role = request.user.user_meta.role.name.lower()
                
                # STRICT ENFORCEMENT: Support agents and admins MUST use the admin panel
                if role in ['support_agent', 'admin']:
                    # Allow access to admin, logout, and static resources only
                    if request.path.startswith('/admin/'):
                        # They're accessing admin, which is allowed
                        pass
                    elif request.path == reverse('logout'):
                        # Allow logout
                        pass
                    else:
                        # Redirect to admin for any other URL
                        messages.warning(request, f"{role.capitalize()} users must use the admin interface.")
                        return redirect('/admin/')
                        
                # Prevent users from accessing admin pages
                if role == 'user' and request.path.startswith('/admin/'):
                    messages.warning(request, 'You do not have permission to access the admin area.')
                    return redirect('dashboard')
                    
            except Exception as e:
                # If role checking fails, proceed normally
                pass
                
        response = self.get_response(request)
        return response
