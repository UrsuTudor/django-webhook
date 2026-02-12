from django.test import TestCase

from .models import Event
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse
import json, hmac, hashlib
from django.conf import settings

def create_event(idempotency_key):
  return Event.objects.create(idempotency_key=idempotency_key)

class EventModelTests(TestCase):
  def test_creates_event_with_idempotency_key(self):
    event = Event(idempotency_key="123")
    self.assertEqual(event.idempotency_key, "123")

  def test_fails_without_idempotency_key(self):
    e = Event()
    with self.assertRaises(ValidationError):
        e.full_clean() 
  
  def test_fails_if_duplicate(self):
    Event.objects.create(idempotency_key="abc")
    with self.assertRaises(IntegrityError):
        Event.objects.create(idempotency_key="abc") 

  def test_if_key_is_too_long(self):
    e = Event.objects.create(idempotency_key = "x" * 256)
    with self.assertRaises(ValidationError):
        e.full_clean()

class ReceiverViewTest(TestCase):
  def test_returns_OK_with_signature(self):
    url = reverse("webhooks:receiver")
    data = { "idempotency_key" : "123"}

    bytes_secret = json.dumps(settings.WEBHOOK_SECRET).encode("utf-8")
    payload_bytes = json.dumps(data).encode("utf-8")
    signature = hmac.new(bytes_secret, payload_bytes, hashlib.sha256).hexdigest()

    response = self.client.post(
      url, 
      data, 
      content_type="application/json",  
      HTTP_EXAMPLE_SIGNATURE=signature
    )
    self.assertEqual(response.status_code, 200)

  def test_returns_401_with_wrong_signature(self):
    url = reverse("webhooks:receiver")
    data = { "idempotency_key" : "123"}

    bytes_secret = json.dumps("fdsahkjt674t1dfgasf").encode("utf-8")
    payload_bytes = json.dumps(data).encode("utf-8")
    signature = hmac.new(bytes_secret, payload_bytes, hashlib.sha256).hexdigest()

    response = self.client.post(
      url, 
      data, 
      content_type="application/json",  
      HTTP_EXAMPLE_SIGNATURE=signature
    )
    self.assertEqual(response.status_code, 401)

  def test_returns_401_with_missing_signature(self):
    url = reverse("webhooks:receiver")
    data = { "idempotency_key" : "123"}

    response = self.client.post(
      url, 
      data, 
      content_type="application/json",  
    )
    self.assertEqual(response.status_code, 401)

  def test_returns_OK_if_event_already_exists(self):
    Event.objects.create(idempotency_key="abc")
    url = reverse("webhooks:receiver")
    data = { "idempotency_key": "abc" }

    bytes_secret = json.dumps(settings.WEBHOOK_SECRET).encode("utf-8")
    payload_bytes = json.dumps(data).encode("utf-8")
    signature = hmac.new(bytes_secret, payload_bytes, hashlib.sha256).hexdigest()

    response = self.client.post(
      url, 
      data, 
      content_type="application/json",  
      HTTP_EXAMPLE_SIGNATURE=signature
    )
    self.assertEqual(response.status_code, 200)

  def test_creates_a_new_event(self):
    url = reverse("webhooks:receiver")
    data = { "idempotency_key": "456" }

    bytes_secret = json.dumps(settings.WEBHOOK_SECRET).encode("utf-8")
    payload_bytes = json.dumps(data).encode("utf-8")
    signature = hmac.new(bytes_secret, payload_bytes, hashlib.sha256).hexdigest()

    response = self.client.post(
      url, 
      data, 
      content_type="application/json",  
      HTTP_EXAMPLE_SIGNATURE=signature
    )

    self.assertIs(Event.objects.filter(idempotency_key="456").exists(), True)
    self.assertEqual(response.status_code, 200)

  def test_fails_without_idempotency_key(self):
    url = reverse("webhooks:receiver")
    data = { "idempotency_key": None }
    
    bytes_secret = json.dumps(settings.WEBHOOK_SECRET).encode("utf-8")
    payload_bytes = json.dumps(data).encode("utf-8")
    signature = hmac.new(bytes_secret, payload_bytes, hashlib.sha256).hexdigest()

    response = self.client.post(
      url, 
      data, 
      content_type="application/json",  
      HTTP_EXAMPLE_SIGNATURE=signature
    )
    self.assertEqual(response.status_code, 400)
