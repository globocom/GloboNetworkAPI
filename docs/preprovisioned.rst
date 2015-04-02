Pre-provisioned Server
######################

The pre provisioned Globo NetworkAPI server uses Vagrant with a Hashicorp Ubuntu 32 bit server.

You can test it locally using this server. We don't recommend running this server in a production environment.

Root password for MySQL database is "password".

GloboNetworkAPI admin user password is "default".

By default, the server will use IP 10.0.0.2/24 in a local network. If this settings conflict with you network environment, you can modify it in the "Vagrantfile", in root directory.

Requirements
************

- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
- [Vagrant](http://www.vagrantup.com/downloads.html) with vagrant Omnibus plugin
```bash
vagrant plugin install vagrant-omnibus)
```
- [Git](http://git-scm.com/downloads)


Setting up the VM
*****************

Execute the following commands:

```bash
$ git clone https://github.com/globocom/GloboNetworkAPI
$ cd GloboNetworkAPI
$ vagrant up
```

The GloboNetworkAPI will be available locally at http://10.0.0.2:8000

The gunicorn logs are at /tmp/gunicorn-*

The Django logs are at /tmp/networkapi.log
