import datetime, socket
from copy import deepcopy

from django.core.mail import (
    EmailMultiAlternatives,
    # mail_admins,
    # send_mail,
    get_connection,
)
from django.conf import settings
from django.db.models import Model
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.template import Template, Context
from django.contrib.auth.models import Group, User

from parameter.models import MailContent
from web.constants import hostname


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


def mailer(**kwargs):
    """
    - kwargs:
        -fields (mandatory)
        - mail_template (mandatory)
        - subject
        - recipient_list (mandatory)
        -  **other : from_email, cc,
    """
    if not "fields" in kwargs:
        raise KeyError("No *fields* in mailer kwargs")

    if not "mail_template" in kwargs:
        raise KeyError("No *mail_template* in mailer kwargs")

    if not "recipient_list" in kwargs:
        raise KeyError("No *recipient_list* in mailer kwargs")

    mail_content = MailContent.objects.first()
    content = mail_content._meta.get_field(kwargs.get("mail_template"))

    if not content:
        raise ValueError("unknown mail_template")

    subject = kwargs.get("subject", "")
    recipient_list = kwargs.get("recipient_list")
    from_email = kwargs.get("from_email", DEFAULT_FROM_EMAIL)
    fields: dict = kwargs.get("fields")

    fields.update(hostname=socket.gethostname())

    if mail_content is not None:
        content_html = render_to_string(
            "includes/email.html",
            context={"subject": subject, "content": content},
        )
        content_html = Template(content_html).render(context=Context(fields))
        content_str = strip_tags(content_html)

    else:
        content_str = " - ".join([str(value) for value in fields.values()])
        content_html = None

    response = send_mail(
        subject=subject,
        message=content_str,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=content_html,
        fail_silently=True,
    )

    return response


def send_task_author_mail(instance, is_created=True):
    subject = "Assignation de tâche"
    subject = subject if is_created else f"(Modification) {subject}"
    to = [author.email for author in instance.author.all()]
    fields = deepcopy(instance.__dict__)

    fields.pop("_state")
    fields.pop("id")
    fields.pop("attachment")
    fields.update(
        author=instance.author,
        assigned_to=instance.assigned_to,
    )

    return mailer(
        subject=subject,
        fields=fields,
        mail_template="mail_task_receiver",
        recipient_list=to,
    )
