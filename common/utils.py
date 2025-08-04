from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_payment_success_email(user, order_id, payment_id, plan_name, assigned_codes, billing_start_date, billing_end_date):
    """
    Sends a payment success confirmation email with assigned codes to the user.
    """
    subject = 'Your Payment Was Successful and Codes Are Assigned!'
    recipient_list = [user.email]
    codes = [code.code for code in assigned_codes]

    context = {
        'user': user,
        'order_id': order_id,
        'payment_id': payment_id,
        'plan_name': plan_name,
        'assigned_codes': assigned_codes,
        'billing_start_date': billing_start_date,
        'billing_end_date': billing_end_date,
    }

    html_message = render_to_string('client/codeemail.html', context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject,
            plain_message,
            None,  # from_email (uses DEFAULT_FROM_EMAIL from settings)
            recipient_list,
            html_message=html_message,
            fail_silently=False,  # Set to True in production to suppress errors
        )
        print(f"Email sent successfully to {user.email} for order {order_id}")
        return True
    except Exception as e:
        print(f"Failed to send email to {user.email} for order {order_id}: {e}")
        # Log the error more comprehensively in a production environment
        return False