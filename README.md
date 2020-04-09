# openldap-ansible
An ansible playbook that uses two roles

## The roles

1. **provision-ec2**

   - Spins up an ec2 instance on AWS (Free tier Ubuntu 18.04)
   
   - Configures ssh keys and a security group with ip filtering, allowing exclusive inbound ssh traffic on port 22.

2. **install-openldap**

   - Installs and configures openldap - ldap-utils & slapd
   
   - Creates a base domain configuration with 2 OU's - Users and Groups. 



## File structure
```bash
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



