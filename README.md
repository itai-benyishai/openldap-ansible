# openldap-ansible
An Ansible project with 2 directories.

- openldap-config is a playbook that provisions and configures an ldap server.

- itai_ldap_module is an Ansible module in python that can search and add users.

## openldap-config

**The Roles**

1. **provision-ec2**

   - Spins up an ec2 instance on AWS (Free tier Ubuntu 18.04)
   
   - Configures ssh keys and a security group with ip filtering, allowing exclusive inbound ssh traffic on port 22.

2. **install-openldap**

   - Installs and configures openldap - ldap-utils & slapd
   
   - Creates a base domain configuration with 2 OU's - Users and Groups. 



## File structure
```bash
openldap-config/
├── hosts
├── playbook.yml
└── roles
    ├── install-openldap
    │   ├── handlers
    │   │   └── main.yml
    │   ├── tasks
    │   │   └── main.yml
    │   ├── templates
    │   │   ├── base.ldif.j2
    │   │   ├── db.ldif.j2
    │   │   └── ldap.conf.j2
    │   └── vars
    │       └── main
    │           ├── ldap_password.yml
    │           └── vars.yml
    └── provision-ec2
        ├── tasks
        │   └── main.yml
        └── vars
            └── main
                ├── aws-keys.yml
                └── main.yml
```

## Prerequisites
- Ansible
- AWS IAM user 
- 2 Ansible vault files:

1. First ansible vault file named:
`roles/provision-ec2/vars/main/aws-keys.yml`

The file's content includes the AWS IAM user's keys: 
 
`ec2_access_key: <access key>`

`ec2_secret_key: <secret key>`

2. Second ansible vault file named:
`roles/install-openldap/vars/main/ldap_password.yml`

The file's content includes the ldap password you want to configure

`ldap_password: <desired-password>`

These ansible vault files are locked with a password and encrypted.
Our password and key variables are safe this way. :)

## The playbook 

To run the playbook: 

`ansible-playbook playbook.yml --ask-vault-pass -i hosts`


## itai_ldap Ansible Module

``` 
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
    
    An Example playbook exists in the directory.
"""



```
