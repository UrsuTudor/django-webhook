from django.shortcuts import render
from django.http import HttpResponse
from .models import Event
import json, hmac, hashlib
from django.conf import settings

def _verify_signature(request):
  signature = request.headers.get("Example-Signature")

  if not signature: return False

  body = request.body
  bytes_secret = json.dumps(settings.WEBHOOK_SECRET).encode("utf-8")

  expected_signature = hmac.new(bytes_secret, body, hashlib.sha256).hexdigest()
  return hmac.compare_digest(signature, expected_signature)

def receiver(request):
  if request.method != "POST": 
    return HttpResponse(status=405) 

  if not _verify_signature(request): 
    return HttpResponse("Wrong signature", status=401)

  data = json.loads(request.body) 
  idempotency_key = data.get("idempotency_key") 

  if not idempotency_key:
    return HttpResponse("Missing idempotency_key", status=400)
  
  if Event.objects.filter(idempotency_key=idempotency_key).exists(): 
    return HttpResponse(status=200) 

  Event.objects.create(idempotency_key=idempotency_key)
  
  return HttpResponse(status=200)

