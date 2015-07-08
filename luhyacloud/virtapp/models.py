from django.db import models

# Create your models here.
class ldapsPara(models.Model):
    uri                 = models.CharField(max_length=100)
    binddn              = models.CharField(max_length=100)
    bindpw              = models.CharField(max_length=100)
    searchbase          = models.CharField(max_length=100)
    domain              = models.CharField(max_length=100)

class virtApp(models.Model):
    uuid             = models.CharField(max_length=100)
    app_display_name = models.CharField(max_length=100)
    app_remote_name  = models.CharField(max_length=100)
    app_exe_path     = models.CharField(max_length=500)
    ecids            = models.CharField(max_length=500)

class vapp_auth(models.Model):
    uuid        = models.CharField(max_length=20)
    role_value  = models.CharField(max_length=100)
    read        = models.BooleanField(default=False)
    write       = models.BooleanField(default=False)
    execute     = models.BooleanField(default=False)
    create      = models.BooleanField(default=False)
    delete      = models.BooleanField(default=False)
