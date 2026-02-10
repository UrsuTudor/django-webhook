from django.shortcuts import render
from django.http import HttpResponse
from .models import Event
import json

def receiver(request):
  if request.method != "POST": 
    return HttpResponse(status=405) 

  data = json.loads(request.body) 
  idempotency_key = data.get("idempotency_key") 

  if not idempotency_key:
    return HttpResponse("Missing idempotency_key", status=400)
  
  if Event.objects.filter(idempotency_key=idempotency_key).exists(): 
    return HttpResponse(status=200) 

  Event.objects.create(idempotency_key=idempotency_key)
  
  return HttpResponse(status=200)

