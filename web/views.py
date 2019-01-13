from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import HostUni, HostCourse, NTUCourse, CourseMatch

# Create your views here.
def index(request):
    courses = NTUCourse.objects.distinct().order_by('code')
    context = {
        'courses': courses,
    }
    return render(request, 'web/base_index.html', context=context)


def about(request):
    return render(request, 'web/base_about.html')


def results(request):
    if request.method == 'POST':
        courses = NTUCourse.objects.distinct().order_by('code')
        queried = [x.strip().upper() for x in request.POST['courses'].split(",")]
        matches = CourseMatch.objects.filter(ntu_course__code__in=queried)
        universities = HostUni.objects.filter(coursematch__ntu_course__code__in=queried).annotate(total_clearable=Count('coursematch__ntu_course__code'), unique_clearable=Count('coursematch__ntu_course__code', distinct=True)).order_by('-unique_clearable', '-total_clearable')
        context = {
            'universities': universities,
            'courses': courses,
            'matches': matches,
        }
        return render(request, 'web/base_results.html', context=context)
    return redirect(index)


def hostuni(request, hostuni_uuid):
    if request.method == 'POST':
        pass
    host_uni = get_object_or_404(HostUni, uuid=hostuni_uuid)
    matches = CourseMatch.objects.filter(host_uni=host_uni)
    context = {
        'host_uni': host_uni,
        'matches': matches,
    }
    return render(request, 'web/base_hostuni.html', context=context)

