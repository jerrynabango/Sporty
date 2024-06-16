import random
import string
import datetime
from django.core.mail import send_mail


def generate_otp(length=6, request=None):
    """
    Generate a random OTP to be in use for 6 minutes else it expires.
    """
    otp = ''.join(random.choices(string.digits, k=length))
    if request:
        # Save the current time in the session
        request.session['otp'] = {
            'otp_code': otp,
            'sent_time': datetime.datetime.now()
        }
    return otp


def send_otp_email(email, otp):
    """Send OTP to the specified email address."""
    subject = "Your OTP for verification"
    message = f"Your OTP is: {otp}\n\nPlease note that this OTP is valid for 5 minutes. If not used within this time, it will expire.\n\nKind regards from E-Sports, CEO Jerry Nabango"
    from_email = "jnabango@gmail.com"
    to_email = [email]

    # Send email
    send_mail(
        subject,
        message,
        from_email,
        to_email,
        fail_silently=False,
    )


# Usage example:
# Generate OTP
otp = generate_otp()

# Send OTP via email
send_otp_email("recipient@example.com", otp)
