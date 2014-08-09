# -*- coding:utf-8 -*-
"""
Title: Infrastructure NetworkAPI
Author: avanzolin / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
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
