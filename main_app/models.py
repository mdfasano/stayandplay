from django.db import models
from django.urls import reverse


# Create your models here.

class Dog(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    weight = models.IntegerField()
    notes = models.TextField(max_length=250)
    
def __str__(self):
    return f'{self.name} ({self.id})'
    
def get_absolute_url(self):
    return reverse('detail', kwargs={'dog_id': self.id})