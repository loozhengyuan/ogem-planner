from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import HostUni, HostCourse, NTUCourse, CourseMatch

approved = [
        'https://sso.wis.ntu.edu.sg/webexe88/owa/sso.asp',
        'https://sso.wis.ntu.edu.sg/webexe88/owa/sso_redirect_pc.asp?t=1&app=https://ogem.zhengyuan.me',
    ]

# Create your views here.
def index(request):
    viewpath = '{scheme}://{host}{path}'.format(scheme=request.scheme, host=request.META['HTTP_HOST'], path=request.path)
    try:
        referer = request.META['HTTP_REFERER']
        if request.META['HTTP_REFERER'] in approved:
            courses = NTUCourse.objects.distinct().order_by('code')
            return render(request, 'web/base_index.html', {'courses': courses})
        else:
            return redirect('https://sso.wis.ntu.edu.sg/webexe88/owa/sso_redirect_pc.asp?t=1&app=https://ogem.zhengyuan.me')
    except KeyError:
        return redirect('https://sso.wis.ntu.edu.sg/webexe88/owa/sso_redirect_pc.asp?t=1&app=https://ogem.zhengyuan.me')


def about(request):
    return render(request, 'web/base_about.html')


def results(request):
    if request.method == 'POST':
        courses = NTUCourse.objects.distinct().order_by('code')
        queried = [x.strip().upper() for x in request.POST['courses'].split(",")]
        matches = CourseMatch.objects.filter(ntu_course__code__in=queried)
        universities = HostUni.objects.filter(coursematch__ntu_course__code__in=queried).annotate(total_clearable=Count('coursematch__ntu_course__code'), unique_clearable=Count('coursematch__ntu_course__code', distinct=True)).order_by('-unique_clearable', '-total_clearable')
        return render(request, 'web/base_results.html', {'universities': universities,
                                                         'courses': courses,
                                                         'matches': matches,})
    return redirect(index)


def hostuni(request, hostuni_uuid):
    if request.method == 'POST':
        pass
    host_uni = get_object_or_404(HostUni, uuid=hostuni_uuid)
    matches = CourseMatch.objects.filter(host_uni=host_uni)
    return render(request, 'web/base_hostuni.html', {'host_uni': host_uni,
                                                        'matches': matches})

