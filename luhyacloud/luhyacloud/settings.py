import os

if os.path.exists('/etc/educloud/modules/clc'):
    from clcsettings import *

if os.path.exists('/etc/educloud/modules/cc'):
    from ccsettings import *
