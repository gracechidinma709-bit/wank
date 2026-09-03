from django.contrib import admin
from .models import UserProfile, Deposit
from .models import SiteSettings
from .models import VerificationPayment
from .models import Transfer


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'email',
        'account_number',
        'currency',
        'balance',
        'verification_fee',
        'transfer_locked',
        'transaction_pin',
        'welcome_email_sent',
    )

    list_editable = (
        'currency',
        'balance',
        'verification_fee',
        'transfer_locked'
    )

    def email(self, obj):
        return obj.user.email
    email.short_description = "Email"
    
    
@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "amount",
        "status",
        "created_at"
    )

    list_filter = ("status",)

    search_fields = (
        "user__username",
        "user__userprofile__account_number",
    )

    list_editable = ("status",)  # 👈 important


@admin.register(VerificationPayment)
class VerificationPaymentAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "amount",
        "status",
        "created_at"
    )

    list_filter = ("status",)

    search_fields = (
        "user__username",
        "user__userprofile__account_number",
    )

    list_editable = ("status",)  # admin picks Pending, Failed, or Successful


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "bank_name",
        "account_number",
        "account_name",
        "amount",
        "status",
        "created_at"
    )

    list_filter = ("status",)

    search_fields = (
        "user__username",
        "user__userprofile__account_number",
        "bank_name",
        "account_number",
        "account_name",
    )

    list_editable = ("status",)  # admin picks Pending, Failed, or Successful


admin.site.register(SiteSettings)