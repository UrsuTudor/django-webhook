import json
from webhooks.models import Event
from django.http import HttpResponse
from .adapters.adapter1 import Adapter1
from .adapters.adapter2 import Adapter2

def get_adapter(service: str):
  adapters = {
      "1": Adapter1,
      "2": Adapter2,
  }

  adapter_class = adapters.get(service)
  if not adapter_class:
      raise Http404("Unknown webhook service")

  return adapter_class()

def receiver(request, service):
  adapter = get_adapter(service)

  if not adapter.verify_signature(request, adapter.secret_key): 
    return HttpResponse("Wrong signature", status=401)

  data = json.loads(request.body) 
  idempotency_key = data.get("idempotency_key") 

  if not idempotency_key:
    return HttpResponse("Missing idempotency_key", status=400)
  
  if Event.objects.filter(idempotency_key=idempotency_key).exists(): 
    return HttpResponse(status=200) 

  Event.objects.create(idempotency_key=idempotency_key)

  adapter.trigger_actions()
  
  return HttpResponse(status=200)

