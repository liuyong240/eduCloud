# coding=UTF-8
#! /usr/bin/python

import os, sys

# this script for Windows ONLY
if __name__ == '__main__':
	url = sys.argv[1]            # arg = "luhyavm://10.0.0.3:3456/"
	ipport = url.split("/")[2]
	cmd_line = "mstsc /f /v:" + ipport
	os.system(cmd_line)
    
    
