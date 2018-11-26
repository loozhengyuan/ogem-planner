from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import HostUni, HostCourse, NTUCourse, CourseMatch, Entries

# Create your views here.
def index(request):
    return render(request, 'web/base_index.html')


def about(request):
    return render(request, 'web/base_about.html')


def results(request):
    if request.method == 'POST':
        queried = [x.strip() for x in request.POST['courses'].split(",")]
        matches = CourseMatch.objects.filter(ntu_course__code__in=queried).annotate(total_clearable=Count('ntu_course__code')).filter(total_clearable__gte=2)
        return render(request, 'web/base_results.html', {'matches': matches})
    return redirect(index)


def hostuni(request, hostuni_id):
    if request.method == 'POST':
        pass
    host_uni = get_object_or_404(HostUni, pk=hostuni_id)
    matches = CourseMatch.objects.filter(host_uni=host_uni)
    return render(request, 'web/base_hostuni.html', {'host_uni': host_uni,
                                                        'matches': matches})

