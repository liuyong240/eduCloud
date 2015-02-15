#! /usr/bin/python


from distutils.core import setup
import py2exe



includes = ["encodings", "encodings.*"]


options = {"py2exe":
    
	{
 "optimize": 2,
     
	  "includes":includes,
          "bundle_files": 1,

          "dist_dir": "luhyavm-webdav-client"
    
    }

}


setup(version = "1.0.0",   
      description = "luhyavm webdav client",
  
    name = "luhyavm webdav client",
  
    options = options,
  
    zipfile = None,
 
      windows=[{"script": "luhyavm-webdav-client.py", }],

) 
