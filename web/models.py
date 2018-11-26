from django.db import models

# Create your models here.
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
