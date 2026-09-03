from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class UserProfile(models.Model):

    CURRENCY_CHOICES = [
        ("USD", "US Dollar ($)"),
        ("GBP", "British Pound (£)"),
        ("NGN", "Nigerian Naira (₦)"),
        ("EUR", "Euro (€)"),
        ("CAD", "Canadian Dollar (C$)"),
        ("AUD", "Australian Dollar (A$)"),
        ("CHF", "Swiss Franc (CHF)"),
        ("BRL", "Brazilian Real (R$)"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=200
    )

    account_number = models.CharField(
        max_length=20,
        unique=True
    )

    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    currency = models.CharField(
        max_length=5,
        choices=CURRENCY_CHOICES,
        default="USD"
    )

    verification_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    transfer_locked = models.BooleanField(
        default=True
    )

    transaction_pin = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )
    
    pin_verified = models.BooleanField(default=False)

    pin_created = models.BooleanField(
        default=False
    )

    welcome_email_sent = models.BooleanField(
        default=False
    )

    profile_picture = CloudinaryField(
        'profile',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # ADD THIS HERE
    @property
    def currency_symbol(self):
        symbols = {
            "USD": "$",
            "GBP": "£",
            "NGN": "₦",
            "EUR": "€",
            "CAD": "C$",
            "AUD": "A$",
            "CHF": "CHF",
            "BRL": "R$",
        }

        return symbols.get(self.currency, "$")

    def __str__(self):
        return f"{self.full_name} - {self.account_number}"
    

class Deposit(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    btc_address = models.CharField(
        max_length=100,
        default="bc1qm9qlahgkrmh0xt92t0ny0p5m568pyn5c6n4l9z"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"
    
    

class Transfer(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    bank_name = models.CharField(max_length=200)

    account_number = models.CharField(max_length=50)

    account_name = models.CharField(max_length=200)

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - Transfer - {self.status}"


class VerificationPayment(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - OTP Verification Fee - {self.status}"


class SiteSettings(models.Model):
    deposit_address = models.CharField(max_length=255)
    btc_qr = models.ImageField(upload_to='qr/')