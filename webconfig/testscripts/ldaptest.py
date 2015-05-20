import ldap
from ldap.controls import SimplePagedResultsControl
import sys
import ldap.modlist as modlist

LDAP_SERVER = "ldaps://192.168.96.128"
BIND_DN = "administrator@educloud.com"
BIND_PASS = "11111111"
USER_FILTER = "(&(objectClass=person)(primaryGroupID=7235))"
USER_BASE = "cn=Users,dc=educloud,dc=com"
PAGE_SIZE = 10


def CreateUser(username, password, base_dn, domain):
    """
    Create a new user account in Active Directory.
    """
    # LDAP connection
    try:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, 0)
        ldap_connection = ldap.initialize(LDAP_SERVER)
        ldap_connection.simple_bind_s(BIND_DN, BIND_PASS)
    except ldap.LDAPError, error_message:
        print "Error connecting to LDAP server: %s" % error_message
        return False

    # Check and see if user exists
    try:
        user_results = ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE,
                                                '(&(sAMAccountName=' +
                                                username +
                                                ')(objectClass=person))',
                                                ['distinguishedName'])
    except ldap.LDAPError, error_message:
        print "Error finding username: %s" % error_message
        return False

    # Check the results
    if len(user_results) != 0:
        print "User", username, "already exists in AD:", \
            user_results[0][1]['distinguishedName'][0]
        return False

    # Lets build our user: Disabled to start (514)
    user_dn = 'cn=' + username + ',' + base_dn
    user_attrs = {}
    user_attrs['objectClass'] = ['top', 'person', 'organizationalPerson', 'user']
    user_attrs['cn'] = username
    user_attrs['userPrincipalName'] = username + '@' + domain
    user_attrs['sAMAccountName'] = username
    user_attrs['displayName'] = username
    user_attrs['userAccountControl'] = '514'
    user_ldif = modlist.addModlist(user_attrs)


    # Add the new user account
    try:
        ldap_connection.add_s(user_dn, user_ldif)
    except ldap.LDAPError, error_message:
        print "Error adding new user: %s" % error_message
        return False


    # Prep the password
    unicode_pass = unicode('\"' + password + '\"', 'iso-8859-1')
    password_value = unicode_pass.encode('utf-16-le')
    add_pass = [(ldap.MOD_REPLACE, 'unicodePwd', [password_value])]
    # 512 will set user account to enabled
    mod_acct = [(ldap.MOD_REPLACE, 'userAccountControl', '512')]
    # New group membership
    #add_member = [(ldap.MOD_ADD, 'member', user_dn)]

    # Add the password
    try:
        ldap_connection.modify_s(user_dn, add_pass)
    except ldap.LDAPError, error_message:
        print "Error setting password: %s" % error_message
        return False

    # Change the account back to enabled
    try:
        ldap_connection.modify_s(user_dn, mod_acct)
    except ldap.LDAPError, error_message:
        print "Error enabling user: %s" % error_message
        return False


    # LDAP unbind
    ldap_connection.unbind_s()

    # All is good
    return True

#ret = CreateUser('lkf', '11111111', 'cn=Users,dc=educloud,dc=com',  'educloud.com')
username = u'likaifeng'
stru = str(username)
print stru