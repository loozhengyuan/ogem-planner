from django.shortcuts import render, redirect
from django.db.models import Count
from .models import Entries

# Create your views here.
def index(request):
    entries = Entries.objects.all()
    return render(request, 'web/base_index.html', {'entries': entries})

def results(request):
    if request.method == 'POST':
        queried = [x.strip() for x in request.POST['courses'].split(",")]
        return render(request, 'web/base_results.html')
    return redirect(index)