import ldap, re
import ldap.modlist as modlist
from ansible.module_utils.basic import *

DOCUMENTATION = """
---
module: itai_ldap
short_description: Add or search ldap users.
description:
    - Add or search for LDAP users. This module has 2 actions, To search
    for a user, and to create a new user.
notes: []
version_added: null
author: Itai Benyishai
requirements:
    - python-ldap
    - python3 (can be resolved in inventory variable) 
      ansible_python_interpreter=/usr/bin/python3

options:
    bind_dn:
        required: True
        description:
            - A DN to bind with.
    bind_pw:
        required: True
        description:
            - The password to use with bind_dn.
    action:
        required: True
        choices: [search, add_user]
        description:
            - The action itai_ldap module will perform.
              'search' action will perform an ldap query for a user.
              'add_user' action will add a user with default attributes:
              objectClass: top, account, posixAccount, shadowAccount
              loginShell: /bin/bash
              other  attributes will be detailed in following parameters.   
    server_uri:
        required: False
        default: ldapi:///
        description:
            - A URI to the LDAP server. The default value lets the underlying
              LDAP client library look for a UNIX domain socket in its default
              location.
    search_user:
        required: False (Is required for search action).
        description:
            - The username you would like to search for.
    ldap_base:
        required: False  (Is required for search action)
        description:
            - The ldap base domain for the search.
    user_dn:
        required: False (Is required for add_user action)
        description:
            - The new user's DN
              must be in syntax: "uid=<user-uid>,ou=<some-ou>,dc=<example>,dc=<com>"
              the ou is optional.
    user_pw:
        required: False (Is required for add_user action)
        default: Aa123456 (So you can change it later. Do not leave this password!)
        description:
            - The new user's password.
              Recommended to input the password encoded in SSHA , with {SSHA} tag.
              Can be passed in cleartext, and will be encoded by ldap server.
              prior to the module, you can use a shell command slappasswd to encode the string
              and register it in a variable.
    uidNumber:
        required: False (Is required for add_user action)
        description:
            - The new user's uidNumber attribute value.
    gidNumber:
        required: False (Is required for add_user action)
        description:
            - The new user's gidNumber attribute value.
    homeDirectory:
        required: False (Is required for add_user action)
        description:
            - The new user's homeDirectory attribute value.
              
"""


EXAMPLES = """
# Search For a User.
- itai_ldap:
    action: "search"
    ldap_base: "dc=itaibenyishai,dc=com"
    bind_dn: "cn=admin,dc=itaibenyishai,dc=com"
    bind_pw: "abc"
    search_user: "ari"
  
# Add a new user.
- itai_ldap:
    action: "add_user"
    bind_dn: "cn=admin,dc=itaibenyishai,dc=com"
    bind_pw: "abc"
    user_dn: "uid=asaf,ou=users,dc=itaibenyishai,dc=com"
    user_pw: {{secret_password}}
    homeDirectory: /home/asaf
    uidNumber: "5001"
    gidNumber: "5001"
"""

# Main

def main():
    fields = {
        "ldap_base": {"required": False, "type": "str"},
        "bind_dn": {"required": True, "type": "str"},
        "bind_pw": {"required": True, "type": "str"},
        "server_uri": {"default": 'ldap:///', "type": "str"},
        "search_user": {"required": False, "type": "str"},
        "user_dn": {"required": False, "type": "str"},
        "user_pw": {"default": "Aa123456", "type": "str"},
        "uidNumber": {"required": False, "type": "str"},
        "gidNumber": {"required": False, "type": "str"},
        "homeDirectory": {"required": False, "type": "str"},
        "action": {
            "required": True,
            "choices": ['search', 'add_user'],
            "type": 'str'
        },
    }
    module = AnsibleModule(argument_spec=fields)
    data = module.params

    # Search choice, Handle errors
    if data['action'] == 'search':
        try:
            result = search(data)
            module.exit_json(changed=True, user=result)
        except ldap.NO_SUCH_OBJECT as error:
            result = "Error. Object not found. Make sure search filter exists under the ldap base."
            module.fail_json(msg=f"{error} {result}")
        except ldap.INVALID_CREDENTIALS as error:
            result = "Error. Invalid Credentials. Make sure bind_dc and bind_pw are correct."
            module.fail_json(msg=f"{error} {result}")
        except ldap.LDAPError as error:
            module.fail_json(msg=error)

    # Add User Choice, Handles errors
    if data['action'] == 'add_user':
        try:
            result = add_user(data)
            module.exit_json(changed=True, meta=result)
        except ldap.ALREADY_EXISTS as error:
            result = "User Already Exists. Did not create user"
            module.exit_json(changed=False, msg=f"{error} {result}")
        except ldap.LDAPError as error:
            module.fail_json(msg=error)
        except IndexError:
            result = "Make sure user DN is in the right syntax. 'uid=<uid>,ou=<ou-name>,dc=<example>,dc=<com>'"
            module.fail_json(msg=result)



#
# Action implementations
#

# Search user function
def search(data):
    # Search filter variable
    search_filter = f'uid={data["search_user"]}'

    # Establish connection and search
    connection = ldap.initialize(data['server_uri'])
    connection.protocol_version = ldap.VERSION3
    connection.simple_bind_s(data['bind_dn'], data['bind_pw'])
    result = connection.search_s(f'{data["ldap_base"]}', ldap.SCOPE_SUBTREE, f'{search_filter}')
    connection.unbind()
    return result


# Add user function
def add_user(data):
    # Grab UID from DN with regex
    name = re.findall(r'uid=(.+?),', str(data['user_dn']))

    # Encode user input for ldap add
    uid = name[0]
    uid = uid.encode()
    pwd = data['user_pw'].encode()
    uidnumber = data['uidNumber'].encode()
    gidnumber = data['gidNumber'].encode()
    homedirectory = data['homeDirectory'].encode()

    # A dict to help build the "body" of the object
    attrs = {'objectclass': [b'top', b'account', b'posixAccount', b'shadowAccount'], 'cn': uid, 'uid': uid,
             'uidNumber': uidnumber, 'gidNumber': gidnumber, 'homeDirectory': homedirectory,
             'loginShell': b'/bin/bash', 'gecos': uid, 'userPassword': pwd, 'shadowLastChange': b'0',
             'shadowMax': b'0', 'shadowWarning': b'0'}

    connection = ldap.initialize(data['server_uri'])
    connection.protocol_version = ldap.VERSION3
    connection.simple_bind_s(data['bind_dn'], data['bind_pw'])

    # Convert our dict to nice syntax for the add-function using modlist-module
    connection.add_s(data['user_dn'], modlist.addModlist(attrs))
    connection.unbind()


main()
