from .base_adapter import BaseAdapter
from django.core.mail import send_mail
from django.tasks import task

class Adapter1(BaseAdapter):
  secret_key="ADAPTER_1_SECRET"

  @task
  def email_users(emails, subject, message, retry_count=0):
    try:
      return send_mail(
          subject=subject, message=message, from_email=None, recipient_list=emails
      )
    except TemporarySMTPError as exc:
      if retry_count < 3:
        email_users.enqueue(
          emails = emails,
          subject = subject,
          message = message,
          retry_count = retry_count + 1
        )
        raise


  def trigger_actions(self, email):
    result = self.email_users.enqueue(
      emails=[email],
      subject="Confirmation email",
      message="Your account was created successfully"
    )

    return result
