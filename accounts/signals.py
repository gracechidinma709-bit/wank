import random

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_save


from .models import UserProfile, Deposit, VerificationPayment, Transfer
from .emails import send_welcome_email, send_transaction_notification


def generate_account_number():
    return str(random.randint(
        1000000000,
        9999999999
    ))


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created:

        UserProfile.objects.create(
            user=instance,
            full_name=instance.get_full_name(),
            account_number=generate_account_number()
        )


@receiver(pre_save, sender=UserProfile)
def handle_transaction_pin_created(sender, instance, **kwargs):

    if not instance.pk:
        return  # brand new profile, no pin yet

    old = UserProfile.objects.get(pk=instance.pk)

    # send the welcome email the first time a transaction PIN is set,
    # so the user has it in hand before they ever log in
    if not old.welcome_email_sent and not old.transaction_pin and instance.transaction_pin:
        send_welcome_email(instance)
        instance.welcome_email_sent = True
        

@receiver(post_save, sender=Deposit)
def notify_deposit_created(sender, instance, created, **kwargs):

    if created:
        send_transaction_notification(
            instance.user.userprofile,
            "deposit",
            instance.amount,
            instance.status,
            extra_line="We'll notify you again once it's confirmed."
        )


@receiver(pre_save, sender=Deposit)
def handle_deposit_status_change(sender, instance, **kwargs):

    if not instance.pk:
        return  # new deposit, ignore for now

    old = Deposit.objects.get(pk=instance.pk)

    if old.status == instance.status:
        return

    # if changed to successful
    if old.status != "successful" and instance.status == "successful":
        profile = instance.user.userprofile
        profile.balance += instance.amount
        profile.save()

    send_transaction_notification(
        instance.user.userprofile,
        "deposit",
        instance.amount,
        instance.status
    )


@receiver(post_save, sender=VerificationPayment)
def notify_verification_payment_created(sender, instance, created, **kwargs):

    if created:
        send_transaction_notification(
            instance.user.userprofile,
            "verification_fee",
            instance.amount,
            instance.status,
            extra_line="We'll notify you again once it's confirmed."
        )


@receiver(pre_save, sender=VerificationPayment)
def handle_verification_payment_status_change(sender, instance, **kwargs):

    if not instance.pk:
        return  # new payment, ignore for now

    old = VerificationPayment.objects.get(pk=instance.pk)

    if old.status == instance.status:
        return

    # once OTP verification fee is confirmed successful, unlock transfers
    if old.status != "successful" and instance.status == "successful":
        profile = instance.user.userprofile
        profile.transfer_locked = False
        profile.save()

    send_transaction_notification(
        instance.user.userprofile,
        "verification_fee",
        instance.amount,
        instance.status
    )


@receiver(post_save, sender=Transfer)
def notify_transfer_created(sender, instance, created, **kwargs):

    if created:
        send_transaction_notification(
            instance.user.userprofile,
            "transfer",
            instance.amount,
            instance.status,
            extra_line=f"To {instance.account_name} - {instance.bank_name}. We'll notify you again once it's confirmed."
        )


@receiver(pre_save, sender=Transfer)
def handle_transfer_status_change(sender, instance, **kwargs):

    if not instance.pk:
        return  # new transfer, ignore for now

    old = Transfer.objects.get(pk=instance.pk)

    if old.status == instance.status:
        return

    # if changed to successful, money has left the account
    if old.status != "successful" and instance.status == "successful":
        profile = instance.user.userprofile
        profile.balance -= instance.amount
        profile.save()

    send_transaction_notification(
        instance.user.userprofile,
        "transfer",
        instance.amount,
        instance.status,
        extra_line=f"To {instance.account_name} - {instance.bank_name}."
    )