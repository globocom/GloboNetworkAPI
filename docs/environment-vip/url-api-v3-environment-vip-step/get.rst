GET
###

Obtaining finality list
***********************

URL::

    /api/v3/environment-vip/step/

Optional GET Parameter::

    environmentp44=[string]

Example:

Without environmentp44 GET Parameter::

    /api/v3/environment-vip/step/

With environmentp44 GET Parameter::

    /api/v3/environment-vip/step/?environmentp44=[string]

where **environmentp44** is a characteristic of environment vips. This argument is not case sensitive. The URL above accepts other GET Parameters, but the type of response will be different depending on what GET Parameters are sent to API. Therefore, to obtain finality list, the URL should have no argument or have the optional environmentp44 argument. Don't forget to encode URL.

Response body:

.. code-block:: json

    [
        {
            "finalidade_txt": <string>
        },...
    ]


Obtaining client list through finality
**************************************

URL::

    /api/v3/environment-vip/step/

Required GET Parameter::

    finality=[string]

Example::

    /api/v3/environment-vip/step/?finality=[string]

where **finality** is a characteristic of environment vips. This argument is not case sensitive. The URL above accepts other GET Parameters, but the type of response will be different depending on what GET Parameters are sent to API. Therefore, to obtain client list ONLY pass **finality** parameter into URL. Don't forget to encode URL.

Response body:

.. code-block:: json

    [
        {
            "cliente_txt": <string>
        },...
    ]


Obtaining environment vip list through finality and client
**********************************************************

URL::

    /api/v3/environment-vip/step/

Required GET Parameters::

    finality=[string]
    client=[string]

Example::

    /api/v3/environment-vip/step/?finality=[string]&client=[string]

where **finality** and **client** are characteristics of environment vips. These arguments are not case sensitive. The URL above accepts other GET Parameters, but the type of response will be different depending on what GET Parameters are sent to API. Therefore, to obtain environment list ONLY pass **finality** and **client** parameters into URL. Don't forget to encode URL. The instruction related to use of extra GET parameters (**kind**, **fields**, **include** and **exclude**) and the default response body is the same as described in :ref:`Environment Vip GET Module <url-api-v3-environment-vip-get>`.

Response body:

.. code-block:: json

    [
        {
            "id": <integer>,
            "finalidade_txt": <string>,
            "cliente_txt": <string>,
            "ambiente_p44_txt": <string>,
            "description": <string>
        },...
    ]

Obtaining environment vip through finality, client and environmentp44
*********************************************************************

URL::

    /api/v3/environment-vip/step/

Required GET Parameters::

    finality=[string]
    client=[string]
    environmentp44=[string]

Example::

    /api/v3/environment-vip/step/?finality=[string]&client=[string]&environmentp44=[string]

where **finality**, **client** and **environmentp44** are characteristics of environment vips. These arguments are not case sensitive . To obtain only one environment vip you must pass the three parameters described above into URL. Don't forget to encode URL. The instruction related to use of extra GET parameters (**kind**, **fields**, **include** and **exclude**) and the default response body is the same as described in :ref:`Environment Vip GET Module <url-api-v3-environment-vip-get>`.

Response body:

.. code-block:: json

    [
        {
            "id": <integer>,
            "finalidade_txt": <string>,
            "cliente_txt": <string>,
            "ambiente_p44_txt": <string>,
            "description": <string>
        },...
    ]





