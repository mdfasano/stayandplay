from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Dog, Service
from .forms import ServiceForm

# Create your views here.
def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')

@login_required
def dogs_index(request):
    dogs = Dog.objects.all()
    return render(request, 'dogs/index.html',
                  {
                      'dogs': dogs,
                  })


@login_required
def dogs_detail(request, dog_id):
    service_form = ServiceForm()
    dog = Dog.objects.get(id=dog_id)
    return render(request, 'dogs/detail.html', {
        'dog': dog,
        'service_form': service_form
        })


class DogCreate(LoginRequiredMixin, CreateView):
    model = Dog
    fields = '__all__'
    success_url = '/dogs/'

class DogUpdate(LoginRequiredMixin, UpdateView):
  model = Dog
  fields = ['breed', 'weight', 'notes']

class DogDelete(LoginRequiredMixin, DeleteView):
  model = Dog
  success_url = '/dogs'


def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in via code
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

def add_service(request, dog_id):
    form = ServiceForm(request.POST)
    if form.is_valid():
        new_service = form.save(commit=False)
        new_service.dog_id = dog_id
        new_service.save()
    return redirect('detail', dog_id=dog_id)

class ServiceDelete(LoginRequiredMixin, DeleteView):
    model = Service

    def get_success_url(self):
        dog_id = self.object.dog_id
        return reverse(
            'detail', 
            kwargs = {'dog_id': dog_id}
        )