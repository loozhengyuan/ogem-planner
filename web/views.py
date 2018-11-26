from django.shortcuts import render
from .models import Entries

# Create your views here.
def index(request):
    entries = Entries.objects.all()
    return render(request, 'web/base_index.html', {'entries': entries})