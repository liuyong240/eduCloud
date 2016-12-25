import requests, json, os
from luhyaapi.settings import *
from luhyaapi.educloudLog import *

import ldap
from ldap.controls import SimplePagedResultsControl
import sys
import ldap.modlist as modlist

logger = geteducloudlogger()

# uri    = "ldaps://10.0.0.21"
# binddn = "administrator@educloud.com"
# bindpw = "1qaz2wsx"
# basedn = 'cn=Users,dc=educloud,dc=com'

class adWrappper():
    def __init__(self, uri, binddn, bindpw, basedn):
        self.uri = uri
        self.binddn = binddn
        self.bindpw = bindpw
        self.basedn = basedn
        self.ldap_connection = None

    def __del__(self):
        self.disconnect()

    def connect(self):
        # LDAP connection
        try:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, 0)
            self.ldap_connection = ldap.initialize(self.uri)
            self.ldap_connection.simple_bind_s(self.binddn, self.bindpw)
            return True
        except ldap.LDAPError, error_message:
            logger.error("Error connecting to LDAP server: %s" % error_message)
            return False

    def disconnect(self):
        # LDAP unbind
        if self.ldap_connection != None:
            self.ldap_connection.unbind_s()

    def isUserExist(self, username):
        try:
            user_results = self.ldap_connection.search_s(self.basedn, ldap.SCOPE_SUBTREE,
                                                '(&(sAMAccountName=' +
                                                username +
                                                ')(objectClass=person))',
                                                ['distinguishedName'])
        except ldap.LDAPError, error_message:
            logger.error("Error finding username: %s" % error_message)
            return False

        # Check the results
        if len(user_results) != 0:
            logger.error( "User" + username + "already exists in AD:" + user_results[0][1]['distinguishedName'][0])
            return True
        else:
            logger.error( "User" + username + "Not find in AD")
            return False

    def AddUser(self, username, password, ou, domain):
        user_dn = 'cn=' + username + ',' + ou
        user_dn = str(user_dn)
        user_attrs = {}
        user_attrs['objectClass'] = ['top', 'person', 'organizationalPerson', 'user']
        user_attrs['cn'] = str(username)
        user_attrs['userPrincipalName'] = str(username + '@' + domain)
        user_attrs['sAMAccountName'] = str(username)
        user_attrs['displayName'] = str(username)
        user_attrs['userAccountControl'] = '514'
        user_ldif = modlist.addModlist(user_attrs)

        # Add the new user account
        try:
            self.ldap_connection.add_s(user_dn, user_ldif)
            logger.error("create user %s succeed." % user_dn )
        except Exception as e:
            logger.error( "Error adding new user: %s" % str(e) )
            return False

        self.SetPass(username, password, ou)

        # Change the account back to enabled
        # 512 will set user account to enabled
        mod_acct = [(ldap.MOD_REPLACE, 'userAccountControl', '512')]
        try:
            self.ldap_connection.modify_s(user_dn, mod_acct)
        except ldap.LDAPError, error_message:
            logger.error("Error enabling user: %s" % error_message)
            return False

        return True

    def SetPass(self, username, password, ou):
        user_dn = 'cn=' + username + ',' + ou
        user_dn = str(user_dn)
        # Prep the password
        unicode_pass = unicode('\"' + str(password) + '\"', 'iso-8859-1')
        password_value = unicode_pass.encode('utf-16-le')
        add_pass = [(ldap.MOD_REPLACE, 'unicodePwd', [password_value])]

        # Add the password
        try:
            self.ldap_connection.modify_s(user_dn, add_pass)
        except ldap.LDAPError, error_message:
            logger.error("Error setting password: %s" % error_message)
            return False

        return True


def isVAPPModuelEnabled():
    if DAEMON_DEBUG == True:
        return True
    else:
        return os.path.exists('/etc/educloud/modules/virtapp')

def list_my_availed_vapp(userid):
    vapps = []
    if not isVAPPModuelEnabled():
        return vapps

    if DAEMON_DEBUG == True:
        url = "http://127.0.0.1:8000/virtapp/api/1.0/listmyvapp"
    else:
        url = "http://127.0.0.1/virtapp/api/1.0/listmyvapp"
    logger.error('list_my_availed_vapp:' + url)
    payload = {
        'uid'   : userid,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def virtapp_addAccount2AD(userid, password):
    if not isVAPPModuelEnabled():
        return

    if DAEMON_DEBUG == True:
        url = "http://127.0.0.1:8000/virtapp/api/1.0/usercreate"
    else:
        url = "http://127.0.0.1/virtapp/api/1.0/usercreate"
    logger.error('virtapp_addAccount2AD:' + url)
    payload = {
        'username'   : userid,
        'password'   : password,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def virtapp_removeAccount2AD(userid):
    if not isVAPPModuelEnabled():
        return

    if DAEMON_DEBUG == True:
        url = "http://127.0.0.1:8000/virtapp/api/1.0/userdelete"
    else:
        url = "http://127.0.0.1/virtapp/api/1.0/userdelete"
    logger.error('virtapp_removeAccount2AD:' + url)
    payload = {
        'username'   : userid,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def virtapp_updateAccount2AD(userid, vapp_en):
    if not isVAPPModuelEnabled():
        return

    if DAEMON_DEBUG == True:
        url = "http://127.0.0.1:8000/virtapp/api/1.0/userupdate"
    else:
        url = "http://127.0.0.1/virtapp/api/1.0/userupdate"
    logger.error('virtapp_updateAccount2AD:' + url)
    payload = {
        'username'   : userid,
        'vapp_en'    : vapp_en,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)

def virtapp_setPassword2AD(userid, password):
    if not isVAPPModuelEnabled():
        return

    if DAEMON_DEBUG == True:
        url = "http://127.0.0.1:8000/virtapp/api/1.0/setpass"
    else:
        url = "http://127.0.0.1/virtapp/api/1.0/setpass"
    logger.error('virtapp_setPassword2AD:' + url)
    payload = {
        'username'   : userid,
        'password'   : password,
    }
    r = requests.post(url, data=payload)
    logger.error(r.content)
    return json.loads(r.content)
