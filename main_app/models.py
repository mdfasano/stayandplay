from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Dog(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    weight = models.IntegerField()
    notes = models.TextField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} ({self.id})'

    def get_absolute_url(self):
        return reverse('detail', kwargs={'dog_id': self.id})

class Photo(models.Model):
    url = models.CharField(max_length=200)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for dog_id: {self.dog_id} @{self.url}"

class Service(models.Model):
    name = models.CharField(max_length=20)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
