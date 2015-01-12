# coding=UTF-8
from basesettings import *
from luhyaapi.educloudLog import *

logger = getclclogger()

# TEMPLATE_DEBUG = True
TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'clc', 'templates'))
logger.error("template dir = %s" % TEMPLATE_DIRS)

INSTALLED_APPS += (
    'clc',
    'walrus',
)

STATICFILES_DIRS += (
    os.path.join(BASE_DIR, "clc", "static"),
)
logger.error("static dir = %s" % str(STATICFILES_DIRS))

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
# sudo apt-get install mysql-server

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', #设置为mysql数据库
        'NAME': 'mysql',  #mysql数据库名
        'USER': 'root',  #mysql用户名，留空则默认为当前linux用户名
        'PASSWORD': 'root',   #mysql密码
        'HOST': '',  #留空默认为localhost
        'PORT': '',  #留空默认为3306端口
    }
}

# login & logout
LOGIN_URL = "/clc/login"
