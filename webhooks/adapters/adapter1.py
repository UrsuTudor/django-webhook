from .base_adapter import BaseAdapter
from django.core.mail import send_mail
from django.tasks import task

class Adapter1(BaseAdapter):
  secret_key="ADAPTER_1_SECRET"

  @task
  def email_users(emails, subject, message):
    return send_mail(
        subject=subject, message=message, from_email=None, recipient_list=emails
    )

  def trigger_actions(self, email):
    result = self.email_users.enqueue(
      emails=[email],
      subject="Confirmation email",
      message="Your account was created successfully"
    )

    return result
