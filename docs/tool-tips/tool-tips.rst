Improve GET requests through some extra parameters
##################################################

When making GET request in V3 routes, you can choose what fields will come into response using the following parameters: **kind**, **fields**, **include** and **exclude**. When none of these parameters are used, NetworkAPI will return a default payload for each module. Depending on your needs, the use of these extra parameters will make your requests faster mainly if you are dealing with many objects. In addition, it is possible to obtain more information about fields that acts as a foreign keys. Look at the examples in each section to understand better.

:ref:`Vip Request <url-api-v3-vip-request-get>` and :ref:`Network IPv4 <url-api-v3-networkv4-get>` modules are used in the examples, consult them to obtain more information about its payload.

Kind parameter
**************

Each module returns a default payload when none of extra parameters are used. With **kind** parameter you can change the default payload to some other two. Look the modules documentation for know about these payloads. **kind** accepts only 'basic' or 'details'. In general, the payload for 'basic' contains little information while 'details' contains so much data.

Suppose that you want to get the basic payload in :ref:`Vip Request <url-api-v3-vip-request-get>`. Use this::

    kind=basic

Fields parameter
****************

The **fields** parameter is used when you want to get only the fields that you specify.

Suppose that you want only id and name fields in :ref:`Vip Request <url-api-v3-vip-request-get>`. Use this::

    fields=id,name

Include parameter
*****************

The include parameter is used to append some field which is not contained on the default payload. Do not use this together **fields**.

Suppose that you want to get the default payload plus 'dscp' and 'equipments' fields in :ref:`Vip Request <url-api-v3-vip-request-get>`. Use this::

    include=dscp,equipments

Exclude parameter
*****************

The exclude parameter is used to remove some field of the default payload. Do not use this together **fields**.

Suppose that you want to get the default payload except 'ipv4' and 'ipv6' fields in :ref:`Vip Request <url-api-v3-vip-request-get>`. Use this::

    exclude=ipv4,ipv6

Using Include and Exclude together
**********************************

Suppose that you want to get the default payload except 'ipv4' field and plus 'dscp' field in :ref:`Vip Request <url-api-v3-vip-request-get>`. Use this::

    exclude=ipv4&include=dscp

Using Kind and Include together
*******************************

Suppose that you want to get the basic payload plus 'dscp' field in :ref:`Vip Request <url-api-v3-vip-request-get>`. Use this::

    kind=basic&include=dscp

Using Kind and Exclude together
*******************************

Suppose that you want to get the details payload except 'ipv4' field in :ref:`Vip Request <url-api-v3-vip-request-get>`. Use this::

    kind=details&exclude=ipv4

Using Kind, Include and Exclude together
****************************************

Suppose that you want to get the basic payload plus 'dscp' field and except 'ipv4' field in :ref:`Vip Request <url-api-v3-vip-request-get>`. Use this::

    kind=basic&include=dscp&exclude=ipv4

Getting more information from fields that acts as a foreign key
***************************************************************

Through **fields** and **include** parameters, you can obtain more information for fields that acts as a foreign key. If you are dealing with such a field, you can through this 'descend or rise' like a tree.

For a simple example, suppose that you make a GET Request for :ref:`Network IPv4 module <url-api-v3-networkv4-get>` to get only vlan field. You certainly would use this::

    fields=vlan

Doing the above, you will get only the identifier of the Vlan. But you want not only the identifier, but also the name of the Vlan. Instead of create a new request for Vlan module, you can at same Network IPv4 request obtain this information. See below how to do this::

    fields=vlan__details

Now, Vlan field is not anymore an integer field, but it is a dictionary with some more information as the vlan name and the identifier of environment related to this Vlan. Let's say now you want the name of this Environment. Again you don't need to create a new request to Environment module, because using the same Network IPv4 request you can get this information. Look below the way to do this::

    fields=vlan__details__environment__basic

Now you have only one JSON with information from various places. In this way you can obtain lots of information in a faster way relieving Network API and reducing time for your application to get a lot of data that is related to each other.

