import requests
from django.conf import settings


def send_welcome_email(profile):
    """
    Sends a "WELCOME TO OUR BANK" email (via Brevo) containing the
    user's transaction PIN, the moment that PIN is set up in admin.
    """

    user = profile.user

    if not user.email:
        return  # nothing to send to

    if not settings.BREVO_API_KEY:
        return  # Brevo not configured, skip silently

    display_name = profile.full_name or user.username

    payload = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [
            {"email": user.email, "name": display_name}
        ],
        "subject": "WELCOME TO OUR BANK",
        "htmlContent": f"""
            <div style="font-family:Arial, sans-serif; max-width:520px; margin:auto;">
                <h2 style="color:#D71E28;">WELCOME TO OUR BANK</h2>
                <p>Hi {display_name},</p>
                <p>Your account has been created successfully. Below are your account details:</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr>
                        <td style="padding:8px; border:1px solid #eee;"><strong>Username</strong></td>
                        <td style="padding:8px; border:1px solid #eee;">{user.username}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px; border:1px solid #eee;"><strong>Account Number</strong></td>
                        <td style="padding:8px; border:1px solid #eee;">{profile.account_number}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px; border:1px solid #eee;"><strong>Transaction PIN</strong></td>
                        <td style="padding:8px; border:1px solid #eee;">{profile.transaction_pin}</td>
                    </tr>
                </table>
                <p>Please keep this PIN confidential. You will need it to verify transactions on your account.</p>
                <p>Thank you for banking with us.</p>
            </div>
        """,
    }

    try:
        requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={
                "accept": "application/json",
                "api-key": settings.BREVO_API_KEY,
                "content-type": "application/json",
            },
            timeout=10,
        )
    except requests.RequestException:
        # never let an email failure block saving the admin change
        pass


TRANSACTION_LABELS = {
    "deposit": "Deposit",
    "verification_fee": "OTP Verification Fee",
    "transfer": "Transfer",
}

STATUS_TITLES = {
    "pending": "Pending",
    "successful": "Successful",
    "failed": "Failed",
}


def send_transaction_notification(profile, transaction_type, amount, status, extra_line=None):
    """
    Sends a notification email (via Brevo) any time a transaction is
    created or its status changes - deposits, transfers, and OTP
    verification fee payments.
    """

    user = profile.user

    if not user.email:
        return  # nothing to send to

    if not settings.BREVO_API_KEY:
        return  # Brevo not configured, skip silently

    display_name = profile.full_name or user.username
    label = TRANSACTION_LABELS.get(transaction_type, transaction_type)
    status_title = STATUS_TITLES.get(status, status.title())
    formatted_amount = f"{profile.currency_symbol}{amount}"

    subject = f"{label} {status_title} - {formatted_amount}"

    status_colors = {
        "pending": "#e8a33d",
        "successful": "#1a9c4a",
        "failed": "#d64545",
    }
    status_color = status_colors.get(status, "#333")

    payload = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [
            {"email": user.email, "name": display_name}
        ],
        "subject": subject,
        "htmlContent": f"""
            <div style="font-family:Arial, sans-serif; max-width:520px; margin:auto;">
                <h2 style="color:#D71E28;">{label} Update</h2>
                <p>Hi {display_name},</p>
                <p>There is an update on your {label.lower()} of <strong>{formatted_amount}</strong>:</p>
                <p style="font-size:18px; font-weight:bold; color:{status_color};">
                    {status_title}
                </p>
                {f'<p>{extra_line}</p>' if extra_line else ''}
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr>
                        <td style="padding:8px; border:1px solid #eee;"><strong>Transaction Type</strong></td>
                        <td style="padding:8px; border:1px solid #eee;">{label}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px; border:1px solid #eee;"><strong>Amount</strong></td>
                        <td style="padding:8px; border:1px solid #eee;">{formatted_amount}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px; border:1px solid #eee;"><strong>Status</strong></td>
                        <td style="padding:8px; border:1px solid #eee; color:{status_color};">{status_title}</td>
                    </tr>
                </table>
                <p>You can view the full details anytime in your Transaction History.</p>
                <p>Thank you for banking with us.</p>
            </div>
        """,
    }

    try:
        requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={
                "accept": "application/json",
                "api-key": settings.BREVO_API_KEY,
                "content-type": "application/json",
            },
            timeout=10,
        )
    except requests.RequestException:
        pass
