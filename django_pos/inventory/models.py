from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Worker model to represent a restaurant employee
class Worker(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=[('chef', 'Chef'), ('staff', 'Staff'), ('manager', 'Manager')])
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ({self.role})'

# Raw Material model to track items
class RawMaterial(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit_of_measurement = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

# Inventory model to track available stock of raw materials
class Inventory(models.Model):
    material = models.OneToOneField(RawMaterial, on_delete=models.CASCADE)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Tracks quantity in stock

    def __str__(self):
        return f'{self.material.name} - {self.stock_quantity} {self.material.unit_of_measurement}'

# Ledger model to track both orders and usages
class Ledger(models.Model):
    TRANSACTION_TYPES = [
        ('order', 'Order'),
        ('usage', 'Usage'),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity ordered or used
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)  # 'order' or 'usage'
    date = models.DateTimeField(auto_now_add=True)  # Date of the transaction
    purpose = models.CharField(max_length=255, blank=True, null=True)  # Purpose for usage (optional)

    def __str__(self):
        return f'{self.transaction_type.capitalize()} - {self.material.name} ({self.quantity}) by {self.worker}'

    def save(self, *args, **kwargs):
        if self.transaction_type == 'usage':
            # Reduce inventory when using materials
            inventory = Inventory.objects.get(material=self.material)
            inventory.stock_quantity -= self.quantity
            inventory.save()
        elif self.transaction_type == 'order':
            # Increase inventory when ordering materials

            print(self.quantity, "self.quantityself.quantityself.quantityself.quantityself.quantity")
            inventory, created = Inventory.objects.get_or_create(material=self.material)
            inventory.stock_quantity += self.quantity
            inventory.save()

        super().save(*args, **kwargs)
