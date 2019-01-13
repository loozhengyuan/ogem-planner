import uuid
from django.db import models

class Base(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

# Create your models here.
class HostUni(Base):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'host university'
        verbose_name_plural = 'host universities'

class NTUCourse(Base):
    code = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'ntu course'
        verbose_name_plural = 'ntu courses'

class HostCourse(Base):
    code = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'host course'
        verbose_name_plural = 'host courses'

class CourseMatch(Base):
    host_uni = models.ForeignKey(HostUni, on_delete=models.CASCADE)
    ntu_course = models.ForeignKey(NTUCourse, on_delete=models.CASCADE)
    host_course = models.ForeignKey(HostCourse, on_delete=models.CASCADE)
    sem_last_offered = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    last_updated = models.CharField(max_length=255)
    validity = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'matched course'
        verbose_name_plural = 'matched courses'
