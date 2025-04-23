# tenant/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class TenantAwareAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        if not hasattr(request, 'tenant'):
            return None
            
        try:
            user = UserModel.objects.get(
                username=username,
                tenant=request.tenant
            )
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None