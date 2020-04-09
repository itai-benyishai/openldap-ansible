# openldap-ansible

An ansible playbook that uses two roles:
1. provision-ec2
   spins up an ec2 instance on AWS (Free tier Ubuntu 18.04)
   configures ssh keys and a security group with ip filtering, allowing exclusive inbound ssh traffic on port 22.

2. install-openldap
   Installs and configures openldap - ldap-utils & slapd
   creates a base domain configuration with 2 OU's - Users and Groups. 
