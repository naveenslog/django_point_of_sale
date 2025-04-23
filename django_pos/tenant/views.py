from django.shortcuts import render

# Create your views here.
from django.contrib.auth.views import LoginView
from django_tenants.utils import tenant_context

class TenantLoginView(LoginView):
    def form_valid(self, form):
        with tenant_context(self.request.tenant):
            return super().form_valid(form)