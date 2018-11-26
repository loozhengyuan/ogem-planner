from django.shortcuts import render, redirect
from django.db.models import Count
from .models import HostUni, HostCourse, NTUCourse, CourseMatch, Entries

# Create your views here.
def index(request):
    entries = Entries.objects.all()
    return render(request, 'web/base_index.html', {'entries': entries})

def results(request):
    if request.method == 'POST':
        queried = [x.strip() for x in request.POST['courses'].split(",")]
        matches = CourseMatch.objects.filter(ntu_course__code__in=queried).annotate(total_clearable=Count('ntu_course__code')).filter(total_clearable__gte=2)
        return render(request, 'web/base_results.html', {'matches': matches})
    return redirect(index)