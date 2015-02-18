import os, sys, wx

if __name__ == '__main__':     
    app = wx.App()
    dlg = wx.TextEntryDialog(None, 'please input user name',  'Connection', '')
    if dlg.ShowModal() == wx.ID_OK:
       user_name = dlg.GetValue()
       url = 'http://10.0.0.11/svn/%s' % user_name
       user_passwd = 'lubos'
       # cmd = 'net use * %s %s /USER:%s' % (url, user_passwd, user_passwd)
       cmd = 'nd2cmd.exe -c m -t dav -u http://10.0.0.11/svn/%s -a %s -p %s -d z' % (user_name, user_passwd, user_passwd)
       cmds = cmd.split()
       os.popen(cmds)
