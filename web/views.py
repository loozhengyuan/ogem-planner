from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import HostUni, HostCourse, NTUCourse, CourseMatch

# Create your views here.
def index(request):
    return render(request, 'web/base_notice.html')
