from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

SERVICES = (
    ('B', 'Bath'),
    ('W', 'Walk'),
    ('T', 'Treat'),
    ('P', 'Playtime')
)

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
    
class Service(models.Model):
    name = models.CharField(
        max_length=1,
        choices=SERVICES,
        default=SERVICES[0][0]
    )
    date = models.DateField('feeding date')

    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    
    def __str__(self):
    # Nice method for obtaining the friendly value of a Field.choice
        return f"{self.get_name_display()} on {self.date}"