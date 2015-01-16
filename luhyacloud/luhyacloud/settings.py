# coding=UTF-8

from basesettings import *
import os

if os.path.exists("/etc/educloud/modules/clc") == True:
    from clcsettings import *
    TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'clc', 'templates'))

    INSTALLED_APPS += (
        'clc',
        'walrus',
    )

    STATICFILES_DIRS += (
        os.path.join(BASE_DIR, "clc", "static"),
    )
else:
    pass

if os.path.exists("/etc/educloud/modules/cc") == True:
    INSTALLED_APPS += (
        'cc',
    )
else:
    pass
