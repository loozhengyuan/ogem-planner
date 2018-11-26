from django.db import models

# Create your models here.
class HostUni(models.Model):
    name = models.CharField(max_length=255)

class HostCourse(models.Model):
    code = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

class NTUCourse(models.Model):
    code = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

class CourseMatch(models.Model):
    host_uni = models.ForeignKey(HostUni, on_delete=models.CASCADE)
    host_course = models.ForeignKey(HostCourse, on_delete=models.CASCADE)
    ntu_course = models.ForeignKey(NTUCourse, on_delete=models.CASCADE)
    sem_last_offered = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    last_updated = models.CharField(max_length=255)
    validity = models.CharField(max_length=255)


class Entries(models.Model):
    host_uni = models.CharField(max_length=255)
    ntu_course_code = models.CharField(max_length=255)
    ntu_course_title = models.CharField(max_length=255)
    host_course_code = models.CharField(max_length=255)
    host_course_title = models.CharField(max_length=255)
    sem_last_offered = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    last_updated = models.CharField(max_length=255)
    validity = models.CharField(max_length=255)