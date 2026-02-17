import json, hmac, hashlib
from django.conf import settings

class BaseAdapter:
  def verify_signature(self, request, secret_key):
    signature = request.headers.get("Example-Signature")

    if not signature: return False

    body = request.body
    bytes_secret = getattr(settings, secret_key).encode("utf-8")

    expected_signature = hmac.new(bytes_secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

  def trigger_actions(self):
    return None
