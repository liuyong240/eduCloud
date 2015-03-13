# coding=UTF-8

from __future__ import absolute_import
import os
from luhyaapi.hostTools import *

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
# CELERY_ACCEPT_CONTENT = ['json']


"""
Django settings for luhyacloud project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

FILE_CHARSET = 'utf-8'
DEFAULT_CHARSET = 'utf-8'
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  #10Mb
FILE_UPLOAD_PERMISSIONS = 0644

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'niy^4ow#z1#)gls#+m0k(f49l6uaiqqt@2+jpb*ey5flqs6bj_'

# SECURITY WARNING: don't run with debug turned on in production!
if os.path.exists("/etc/educloud/modules/core") == True:
    DEBUG = False
    TEMPLATE_DEBUG = False
else:
    DEBUG = True
    TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1'
]

nics = getHostNetInfo()
if nics['ip0'] != '':
    ALLOWED_HOSTS.append(nics['ip0'])
if nics['ip1'] != '':
    ALLOWED_HOSTS.append(nics['ip1'])
if nics['ip2'] != '':
    ALLOWED_HOSTS.append(nics['ip2'])
if nics['ip3'] != '':
    ALLOWED_HOSTS.append(nics['ip3'])

# Application definition
INSTALLED_APPS = (
     'django.contrib.admin',
     'django.contrib.auth',
     'django.contrib.contenttypes',
     'django.contrib.sessions',
     'django.contrib.messages',
     'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ROOT_URLCONF = 'luhyacloud.urls'

WSGI_APPLICATION = 'luhyacloud.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

# add LOCAL_PATHS for Chinese Version.
# by default it is commented for English version.
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'conf/locale'),
)

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-CN'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

SESSION_COOKIE_AGE = 86400
