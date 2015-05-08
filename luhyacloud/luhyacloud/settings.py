# coding=UTF-8

from basesettings import *
import os

if DEBUG == True:
    INSTALLED_APPS += (
        'portal',
        'clc',
        'walrus',
        'cc',
        'virtapp',
    )

    from clcsettings import *

    TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'portal',   'templates'))
    TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'clc',      'templates'))
    TEMPLATE_DIRS.append(os.path.join(BASE_DIR, 'virtapp',  'templates'))

    STATICFILES_DIRS += (
        os.path.join(BASE_DIR, 'portal', "static"),
        os.path.join(BASE_DIR, "clc", "static"),
        os.path.join(BASE_DIR, "virtapp", "static"),
    )
    LOCALE_PATHS += (
        os.path.join(BASE_DIR, 'portal', 'conf/locale'),
        os.path.join(BASE_DIR, 'clc',    'conf/locale'),
        os.path.join(BASE_DIR, 'virtapp','conf/locale'),
    )
else:
    if os.path.exists("/etc/educloud/modules/portal") == True:
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

    if os.path.exists("/etc/educloud/modules/clc") == True:
        from virtappsettings import *

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
        INSTALLED_APPS += (
            'walrus',
        )

    if os.path.exists("/etc/educloud/modules/cc") == True:
        INSTALLED_APPS += (
            'cc',
        )
