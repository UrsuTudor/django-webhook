from django.db import models

class Event(models.Model):
    idempotency_key = models.CharField(max_length=255, unique=True, blank=False, null=False)

    def __str__(self):
        return self.idempotency_key
