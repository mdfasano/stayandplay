import os
import re
import uuid
import boto3
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Dog, Service, Photo
from .forms import ServiceForm

# Create your views here.
def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')

@login_required
def dogs_index(request):
    # dogs = Dog.objects.all()
    dogs = Dog.objects.filter(user=request.user)
    return render(request, 'dogs/index.html',{'dogs': dogs })

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
    fields = ['name', 'breed', 'weight', 'notes']
    success_url = '/dogs/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DogUpdate(LoginRequiredMixin, UpdateView):
    model = Dog
    fields = ['breed', 'weight', 'notes']

    def form_valid(self, form):
        if self.object.user == self.request.user:
            return super().form_valid(form)
        else:
            # possibly make an error rendering page for cases like this
            return render(self.request, 'home.html')

class DogDelete(LoginRequiredMixin, DeleteView):
  model = Dog
  success_url = '/dogs'

@login_required
def add_photo(request, dog_id):
    # photo-file maps to the "name" attr on the <input>
    photo_file = request.FILES.get("photo-file", None)
    if photo_file:
        s3 = boto3.client("s3")
        # Need a unique "key" (filename)
        # It needs to keep the same file extension
        # of the file that was uploaded (.png, .jpeg, etc.)
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind(".") :]
        try:
            bucket = os.environ["S3_BUCKET"]
            s3.upload_fileobj(photo_file, bucket, key)
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            Photo.objects.create(url=url, dog_id=dog_id)
        except Exception as e:
            print("An error occurred uploading file to S3")
            print(e)
    return redirect("detail", dog_id=dog_id)

@login_required
def del_photo(request, dog_id):
    client = boto3.client('s3')
    bucket = os.environ["S3_BUCKET"]
    photo = Photo.objects.get(dog_id=dog_id)

    # Delete from postgres
    photo.delete()

    # Delete from AWS
    # photo.url looks like this: 
    #   https://s3.us-east-2.amazonaws.com/stayandplay/c74742.png
    # Grab only the part at the end: 
    #   stayandplay/c74742.png
    # Finally, skip over 'stayandplay/' to get:
    #   c74742.png
    x = re.search('stayandplay/.*$',photo.url)
    filename = x.group()[12:]

    try:
        client.delete_object(
            Bucket=bucket,
            Key=filename
        )
    except Exception as ex:
        print(str(ex))

    return redirect("detail", dog_id=dog_id)

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

@login_required
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

class ServiceUpdate(LoginRequiredMixin, UpdateView):
    model = Service
    fields = ['date', 'name']

@login_required
def searchbar(request):
    query = request.GET.get('query', '')
    matches = Dog.objects.filter(user=request.user)
    matches = matches.filter(name__icontains=query)
    
    return render(request, 'dogs/index.html', {'dogs': matches } )