GloboNetworkAPI
===============

[![Build Status](https://travis-ci.org/globocom/GloboNetworkAPI.svg)](https://travis-ci.org/globocom/GloboNetworkAPI)
[![Documentation Status](https://readthedocs.org/projects/globonetworkapi/badge/?version=latest)](https://globonetworkapi.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Globo NetworkAPI is a REST API that manages IP networking resources. It is supposed to be not just an IPAM, but a centralized point of network control, allowing documentation from physical and logical network and starting configuration requests to equipments.

Globo NetworkAPI is made to support a Web User Interface features, exposing its functionality to be used with any other client.

This web tool helps network administrator manage and automate networking resources (routers, switches and load balancers) and document logical and physical networking.

They were created to be vendor agnostic and to support different orchestrators and environments without loosing the centralized view of all network resources allocated.

It was not created to be and inventory database, so it does not have CMDB functionalities.

## Features

* LDAP authentication
* Supports cabling documentation (including patch-panels/DIO’s)
* Separated Layer 2 and Layer 3 documentation (vlan/network)
* IPv4 and IPv6 support
* Automatic allocation of Vlans, Networks and IP’s
* ACL (access control list) automation (documentation/versioning/applying)
* Load-Balancer support
* Automated deploy of allocated resources on switches, routers and load balancers
* Load balancers management
* Expandable plugins for automating configuration

## Documentation
[Documentation](http://globonetworkapi.readthedocs.org/)

## How to contribute
Check this out at
[Contributing](https://github.com/globocom/GloboNetworkAPI/blob/master/CONTRIBUTING.md) file.

## Authors
[Authors](./AUTHORS.md)
