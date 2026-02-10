from django.test import TestCase

from .models import Event
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

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
