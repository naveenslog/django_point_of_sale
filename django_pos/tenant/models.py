from django_tenants.models import TenantMixin, DomainMixin
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

class TenantUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not extra_fields.get("tenant"):
            raise ValueError("Tenant must be set when creating a TenantUser.")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    # required for schema separation
    auto_create_schema = True

class Domain(DomainMixin):
    pass

class TenantUser(AbstractUser):
    tenant = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name='users',
        editable=True
    )

    class Meta:
        unique_together = ('tenant', 'username')
    
    objects = TenantUserManager() 
    # def save(self, *args, **kwargs):
    #     """Override save to handle tenant updates properly"""
    #     # Add any pre-save validation here if needed
    #     # if not self.tenant_id:
    #     #     raise ValueError("Tenant must be set for TenantUser")
            
    #     super().save(*args, **kwargs)
    
    # @classmethod
    # def get_by_natural_key(cls, username):
    #     """Override for proper lookup during authentication"""
    #     return cls.objects.get(username=username)