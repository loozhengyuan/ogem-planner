from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import HostUni, HostCourse, NTUCourse, CourseMatch

# Create your views here.
def index(request):
    return render(request, 'web/base_index.html')


def about(request):
    return render(request, 'web/base_about.html')


def results(request):
    if request.method == 'POST':
        queried = [x.strip().upper() for x in request.POST['courses'].split(",")]
        universities = HostUni.objects.filter(coursematch__ntu_course__code__in=queried).annotate(total_clearable=Count('coursematch')).order_by('-total_clearable')
        return render(request, 'web/base_results.html', {'universities': universities})
    return redirect(index)


def hostuni(request, hostuni_uuid):
    if request.method == 'POST':
        pass
    host_uni = get_object_or_404(HostUni, uuid=hostuni_uuid)
    matches = CourseMatch.objects.filter(host_uni=host_uni)
    return render(request, 'web/base_hostuni.html', {'host_uni': host_uni,
                                                        'matches': matches})

