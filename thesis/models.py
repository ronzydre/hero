from django.db import models
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=250)
    interest = ArrayField(ArrayField(models.CharField(max_length=250)))

    def __str__(self):
        return self.name + '    ' + self.interest
