#! /usr/bin/python

from distutils.core import setup
import py2exe

includes = ["encodings", "encodings.*"]

options = {"py2exe":
    {
     "optimize": 2,
     "includes":includes,
     "bundle_files": 1,
     "dist_dir": "luhyavm-handler"
    }
}

setup(  
    version = "1.0.0",  
    description = "luhyavm handler",  
    name = "luhyavm handler",  
    options = options,
    zipfile = None,
    windows=[{"script": "luhyavm-windows-handler.py", 
               }], 
) 
