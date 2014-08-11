# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
"""

from django.db.models import Q


def build_query_to_datatable(querySet, asortingCols, customSearch, searchableColumns, startRecord, endRecord):
    """
    Build query using params received
    """

    if asortingCols is not None and len(asortingCols) > 0:
        # Ordering data
        querySet = querySet.order_by(*asortingCols)

    if not querySet.ordered:
        querySet = querySet.order_by("pk")

    # Apply filtering by value sent by user
    if customSearch != None:
        outputQ = None
        for searchableColumn in searchableColumns:
            kwargz = {searchableColumn + "__icontains": customSearch}
            outputQ = outputQ | Q(**kwargz) if outputQ else Q(**kwargz)
        querySet = querySet.filter(outputQ)

    total = querySet.count()
    # Slice pages
    querySet = querySet[startRecord:endRecord]

    # Return data paginated and total of records
    return querySet, total
