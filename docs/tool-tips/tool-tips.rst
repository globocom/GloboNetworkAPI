Improve GET requests through some extra parameters
##################################################

When making GET request in V3 routes, you can choose what fields will come into response using the following parameters:
**kind**, **fields**, **include** and **exclude**. When none of these parameters are used, NetworkAPI will return a default payload
for each module. Depending on your needs, the use of these extra parameters will make your requests faster mainly if you
are dealing with many objects.

Kind parameter
**************

Each module returns a default payload when none of extra parameters are used. With **kind** parameter you can change the
default payload to some other two. Look the modules documentation for know about these payloads. **kind** accepts only
'basic' or 'details'. In general, the payload for 'basic' contains little information while 'details' contains so much data.

Fields parameter
****************

The **fields** parameter is used when you want to get only the fields that you specify.

Include parameter
*****************

The include parameter is used to append some field which is not contained on the default payload. Consulting the
documentation of each module you can know which fields are brought by default. Do not use this together **fields**.

Exclude parameter
*****************

The exclude parameter is used to remove some field of the default payload. Consulting the documentation of each module
you can know which fields are brought by default. Do not use this together **fields**.

Getting specific fields in more detailed way
********************************************

Through **fields**, **include** and **exclude** parameters, you can obtain more information for fields that acts as
a foreign key. If you are dealing with such a field, you can through this 'descend or rise' like a tree. For a simple
example, suppose that you make a GET Request for Network IPv4 module using fields=vlan. Doing this, vlan field in response
will have an integer value which corresponds to identifier of the related Vlan. But you want not only the identifier,
but also the name of the Vlan. Instead using fields=vlan you can use fields=vlan__details. If you
make this request, you will see that vlan field no more represents an integer, but now a dictionary with some informations.
Now you are also interested in the environment associated to this Vlan. Using
fields=vlan__details you can only get the identifier of this Environment. Not satisfied, you want the name of this
Environment. So you can substitute fields=vlan__details by fields=vlan__details__environment__basic. Now, you have only
one JSON with information from various places.

Some Examples to help you better understand
*******************************************

Here is presented some examples for Vip Request module. Please check the available fields, the default payload and the payloads for 'basic' and 'details'
kind in Vip Request documentation (link).

Suppose that you want to get the default payload plus 'dscp' and 'equipments' fields. Use this::

    include=dscp,equipments

Suppose that you want to get the default payload except 'ipv4' and 'ipv6' fields. Use this::

    exclude=ipv4,ipv6

Suppose that you want to get the default payload except 'ipv4' field and plus 'dscp' field. Use this::

    exclude=ipv4&include=dscp

Suppose that you want only id and name fields. Use this::

    fields=id,name

