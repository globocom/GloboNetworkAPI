
.. _acl_through_sdn_ref:

Access Control Lists (ACLs)
###########################

Globo Network API enables deployment of *Access Control lists* on
OpenVSwitch_ through the OpenFlow_ controller OpenDaylight_.

To do it, Globo Network API exports HTTP urls to manage *flows* of ACLs.
Using the abstraction of a :ref:`environment`, we segment the ACLs.

When a controller is inserted as a new equipment in the API we must inform
for which Environment that controller belongs. This way we segment which
Environment will use ACLs based on SDN.

If you run a set of OpenVSwitches and control them with the controller you
should use the following HTTP Urls to manage ACLs flows inside the virtual
switch:

.. toctree::
   url-api-v4-sdn-acl/get
   url-api-v4-sdn-acl/post
   url-api-v4-sdn-acl/put
   url-api-v4-sdn-acl/delete


.. _OpenVSwitch: http://openvswitch.org

.. _OpenDaylight: https://www.opendaylight.org/

.. _OpenFlow: https://www.opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.5.1.pdf

