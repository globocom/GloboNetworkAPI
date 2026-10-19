.. _url-api-v4-template-get:

GET
###

Obtaining the content of a template
***********************************

Returns the exact content of a template file as plain text
(``Content-Type: text/plain; charset=utf-8``).

URL::

    /api/v4/templates/[template_type]/[file_path]/

where:

* **template_type** is the type of template. Accepted values:

  * *config* - configuration templates (network, interface and BGP). The root
    directory is defined by the ``NETWORKAPI_CONFIG_TEMPLATE_PATH``
    environment variable.
  * *rack* - rack provisioning templates. The root directory is defined by the
    ``path_to_guide`` system variable.

* **file_path** is the path of the template relative to the root directory of
  its type. Subdirectories are separated by slashes.

Example::

    /api/v4/templates/config/bgp/template_neighbor_v4_remove_junos/

The response body is the content of the template file, without changes.

Restrictions on **file_path**
=============================

Only plain relative paths are accepted. Requests are rejected when
**file_path**:

* is an absolute path;
* contains backslashes or null bytes;
* contains empty, ``.`` or ``..`` segments;
* resolves to a file outside the root directory of the template type.

Errors
======

======  ==================================================================
Status  Reason
======  ==================================================================
400     Invalid **file_path** (see restrictions above).
401     Missing or invalid credentials.
404     Template not found in the root directory of the template type, or
        **template_type** is not *config* or *rack*.
500     The template file exists but could not be read.
======  ==================================================================

Error response body example:

.. code-block:: json

    {
        "detail": "Template bgp/template_neighbor_v4_remove_junos not found."
    }

Local development
=================

With docker compose, the containers read *config* templates from
``/templates/config/``. By default, this directory is mounted from
``networkapi/config_templates/`` in this repository.

To use templates from another directory on your machine, for example a local
clone of the templates repository, create a ``.env`` file in the root of the
project:

.. code-block:: bash

    NETWORKAPI_CONFIG_TEMPLATE_PATH=../networkapi_config_templates

Then recreate the containers:

.. code-block:: bash

    docker-compose up -d netapi celery

The ``.env`` file is only read by docker compose on your machine. Do not
commit it.
