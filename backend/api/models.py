from django.db import models
from decimal import Decimal

class PaymentMethod(models.TextChoices):
    PIX = 'PIX', 'PIX'
    TED = 'TED', 'TED'
    TRANSFER = 'TRANSFER', 'Bank Transfer'

class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PAID = 'PAID', 'Paid'
    CANCELLED = 'CANCELLED', 'Cancelled'

class Provider(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    salary_base = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices, 
        default=PaymentMethod.PIX
    )
    
    # Banking Details
    pix_key = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_agency = models.CharField(max_length=20, blank=True, null=True)
    bank_account = models.CharField(max_length=30, blank=True, null=True)
    
    email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='payments')
    reference = models.CharField(max_length=50, help_text="e.g. 01/2026")
    
    amount_base = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounts = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    total_calculated = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    
    paid_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate total before saving
        self.total_calculated = (self.amount_base or Decimal(0)) + (self.bonus or Decimal(0)) - (self.discounts or Decimal(0))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider.name} - {self.reference} ({self.status})"
