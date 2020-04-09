# openldap-ansible

## The roles

An ansible playbook that uses two roles:
1. provision-ec2
   spins up an ec2 instance on AWS (Free tier Ubuntu 18.04)
   
   configures ssh keys and a security group with ip filtering, allowing exclusive inbound ssh traffic on port 22.

2. install-openldap
   Installs and configures openldap - ldap-utils & slapd
   
   creates a base domain configuration with 2 OU's - Users and Groups. 



## File structure

openldap-ansible/
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

## Pre-requisits
- Ansible
- AWS IAM user 
- 2 Ansible vault files:

`roles/provision-ec2/vars/main/aws-keys.yml`

with AWS IAM user's keys: 
 
`ec2_access_key: <access key>`

`ec2_secret_key: <secret key>`

and another ansible vault file:

`roles/install-openldap/vars/main/ldap_password.yml`

with the ldap password you want to configure

`ldap_password: <desired-password>`

that way these files are locked with a password and encrypted. 

## The playbook 

To run the playbook: 

`ansible-playbook playbook.yml --ask-vault-pass -i hosts`



