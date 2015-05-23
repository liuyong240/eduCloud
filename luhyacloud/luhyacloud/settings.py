# coding=UTF-8

from basesettings import *
import os

if os.path.exists("/etc/educloud/modules/portal") == True:
    logger.error('/etc/educloud/modules/portal Exist ..')
    TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'portal', 'templates'))
    INSTALLED_APPS += (
        'portal',
    )
    STATICFILES_DIRS += (
        os.path.join(BASE_DIR, 'portal', "static"),
    )
    LOCALE_PATHS += (
        os.path.join(BASE_DIR, 'portal', 'conf/locale'),
    )

if os.path.exists("/etc/educloud/modules/clc") == True:
    logger.error('/etc/educloud/modules/clc Exist ..')
    from clcsettings import *

    TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'clc',    'templates'))

    INSTALLED_APPS += (
        'clc',
    )
    STATICFILES_DIRS += (
        os.path.join(BASE_DIR, "clc", "static"),
    )
    LOCALE_PATHS += (
        os.path.join(BASE_DIR, 'clc',    'conf/locale'),
    )

if os.path.exists("/etc/educloud/modules/virtapp") == True:
    logger.error('/etc/educloud/modules/virtapp Exist ..')
    TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'virtapp',    'templates'))
    INSTALLED_APPS += (
        'virtapp',
    )
    STATICFILES_DIRS += (
        os.path.join(BASE_DIR, "virtapp", "static"),
    )
    LOCALE_PATHS += (
        os.path.join(BASE_DIR, 'virtapp',    'conf/locale'),
    )

if os.path.exists("/etc/educloud/modules/walrus") == True:
    logger.error('/etc/educloud/modules/walrus Exist ..')
    INSTALLED_APPS += (
        'walrus',
    )

if os.path.exists("/etc/educloud/modules/cc") == True:
    logger.error('/etc/educloud/modules/cc Exist ..')
    INSTALLED_APPS += (
        'cc',
    )

logger.error('TEMPLATE_DIRS     = %s' % TEMPLATE_DIRS)
logger.error('INSTALLED_APPS    = %s' % str(INSTALLED_APPS))
logger.error('STATICFILES_DIRS  = %s' % str(STATICFILES_DIRS))
logger.error('LOCALE_PATHS      = %s' % str(LOCALE_PATHS))
