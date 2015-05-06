from django.db import models

# Create your models here.
class ldapsPara(models.Model):
    uri                 = models.CharField(max_length=100)
    binddn              = models.CharField(max_length=100)
    bindpw              = models.CharField(max_length=100)
    searchbase          = models.CharField(max_length=100)

class virtApp(models.Model):
    appName = models.CharField(max_length=100)
    appPath = models.CharField(max_length=500)
    ecid    = models.CharField(max_length=20)
