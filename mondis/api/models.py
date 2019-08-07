from django.db import models
from django.db.models import deletion

from api.constants import PERSON_CHOICES, HOUR_CHOICES, USERNAME_MAX_LENGTH, HOUR_MAX_LENGTH


class Person(models.Model):
    username = models.CharField(max_length=USERNAME_MAX_LENGTH, unique=True)
    person_type = models.SmallIntegerField(choices=PERSON_CHOICES)

    def __str__(self):
        return self.username


class Slot(models.Model):
    hour = models.CharField(choices=HOUR_CHOICES, max_length=HOUR_MAX_LENGTH)
    added_by = models.ForeignKey(Person, on_delete=deletion.CASCADE)
    added_at = models.DateField()

    class Meta:
        unique_together = ['hour', 'added_by', 'added_at']


class Event(models.Model):
    users = models.ManyToManyField(Person)
    slot = models.ForeignKey(Slot, on_delete=deletion.CASCADE)
