from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, get_connection  # mail_admins,
from django.db.models import Model
from django.http import HttpRequest
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from parameter.models import MailContent
from xauth.models import User

DEFAULT_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", None)


def send_mail(
    subject,
    message,
    from_email,
    recipient_list,
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    connection=None,
    html_message=None,
    cc=None,
):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(
        subject, message, from_email, recipient_list, connection=connection, cc=cc
    )
    if html_message:
        mail.attach_alternative(html_message, "text/html")

    return mail.send()


def mailer(subject, recipient_list, content, from_email=None, cc=None, **kwargs):
    """
    - subject (mandatory)
    - recipient_list (mandatory)
    - content (mandatory) - the actual content of the email
    - from_email (optional)
    - cc (optional)
    """

    if not recipient_list:
        raise KeyError("No recipient_list in mailer kwargs")

    # Default sender email
    from_email = from_email or DEFAULT_FROM_EMAIL

    # Prepare the email content
    content_html = render_to_string("email.html", context={"subject": subject, "content": content})
    
    # Prepare plain text version
    content_str = strip_tags(content_html)

    # Send the email
    response = send_mail(
        subject=subject,
        message=content_str,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=content_html,
        fail_silently=True,
        cc=cc,
    )

    return response



def send_account_activation_mail(request: HttpRequest, instance: User, link):
    subject = "Code d'activation de compte"
    to = [instance.email]
    
    # Prepare the content of the email
    content = f"""
    Bonjour {instance.first_name} {instance.last_name},

    Merci de vous être inscrit. Pour activer votre compte, veuillez utiliser le lien ci-dessous :

    {link}

    Si vous avez des questions, n'hésitez pas à nous contacter.

    Cordialement,
    L'équipe de support
    """

    # Send the email using the mailer function
    return mailer(
        subject=subject,
        recipient_list=to,
        content=content,
        from_email=None,  # or set to your default email if needed
    )

