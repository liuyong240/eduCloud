#! /usr/bin/python
# coding=UTF-8

import os, sys
import wx

# this script for Windows ONLY
if __name__ == '__main__':
    url = sys.argv[1]            # arg = "luhyavm://18ebabc2"
    imgid = url.split("//")[1]

    # check imgid is exist
    imgFile = "/storage/images/%s/machine" % imgid
    if os.path.exists(imgFile):
        # cmd_line = "nmcli nm enable true"
        # os.system(cmd_line)     
        cmd_line = "wmctrl -a firefox; xdotool key alt+F4"
        os.system(cmd_line)
        cmd_line = "/storage/bin/clientMain.py " + imgid
        os.system(cmd_line)
    else:
        app = wx.App()
        dlg = wx.MessageDialog(None, "选定的虚拟机文件本地不存在，请联系管理员！", "注意：", wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()
    
    
    
    
