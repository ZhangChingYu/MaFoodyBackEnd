from django.db import models

# Create your models here.


class Pictures(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='files/cover')

class DBTest(models.Model):
    TestId = models.AutoField(primary_key=True)
    TestName = models.CharField(max_length=255)

class Avatar(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='files/avatar') 
    