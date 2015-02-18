# coding=UTF-8

from basesettings import *
import os

if os.path.exists("/etc/educloud/modules/clc") == True:
    from clcsettings import *
    TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'portal', 'templates'))
    TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'clc',    'templates'))

    INSTALLED_APPS += (
        'portal',
        'clc',
        'walrus',
    )

    STATICFILES_DIRS += (
        os.path.join(BASE_DIR, 'portal', "static"),
        os.path.join(BASE_DIR, "clc", "static"),
    )

    LOCALE_PATHS += (
        os.path.join(BASE_DIR, 'portal', 'conf/locale'),
        os.path.join(BASE_DIR, 'clc',    'conf/locale'),
    )
else:
    pass

if os.path.exists("/etc/educloud/modules/cc") == True:
    INSTALLED_APPS += (
        'cc',
    )
else:
    pass
