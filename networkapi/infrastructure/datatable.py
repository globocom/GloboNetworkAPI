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
from django.db.models import Q


def build_query_to_datatable(query_set, asorting_cols, custom_search,
                             searchable_columns, start_record, end_record):
    """
    Build query using params received
    """

    if asorting_cols is not None and len(asorting_cols) > 0:
        # Ordering data
        query_set = query_set.order_by(*asorting_cols)

    if not query_set.ordered:
        query_set = query_set.order_by("pk")

    # Apply filtering by value sent by user
    if custom_search is not None:
        output_q = None
        for searchableColumn in searchable_columns:
            kwargz = {searchableColumn + "__icontains": custom_search}
            output_q = output_q | Q(**kwargz) if output_q else Q(**kwargz)
        query_set = query_set.filter(output_q)

    query_set = query_set.distinct()

    total = query_set.count()
    # Slice pages
    query_set = query_set[start_record:end_record]

    # Return data paginated and total of records
    return query_set, total


def build_query_to_datatable_v3(query_set, search={}):
    """
    Build query using params received and return with dict

    :param query_set: Object "query" with data
    :param search.extends_search: Permmit to filter objects by relationship or
    :param search.asorting_cols: List of fields to use in "order_by"
    :param search.custom_search: Value generic to search in some fields
    :param search.searchable_columns: List of fields used in "generic search"
    :param search.start_record: Value used in initial "limit"
    :param search.end_record: Value used in final "limit
    :return obj_map.total: Total objects returned
    :return obj_map.next_search: Copy of search
    :return obj_map.next_search.start_record: Value to use in initial "limit"
        in next search(add 25)
    :return obj_map.next_search.end_record: Value to use in final "limit"
        in next search(add 25)
    :return obj_map.prev_search.start_record: Value to use in initial "limit"
        in prev search(remove 25 of value received)
    :return obj_map.prev_search.end_record: Value to use in final "limit"
        in prev search(remove 25 of value received)
    """

    if search.get('extends_search'):
        query_set = query_set.filter(reduce(
            lambda x, y: x | y, [Q(**item) for item in search.get('extends_search')]))

    search_query = dict()
    search_query["extends_search"] = search.get('extends_search') or []
    search_query["asorting_cols"] = search.get("asorting_cols") or ["-id"]
    search_query["custom_search"] = search.get("custom_search") or None
    search_query["searchable_columns"] = search.get("searchable_columns") or []
    search_query["start_record"] = search.get("start_record") or 0
    search_query["end_record"] = search.get("end_record") or 25

    query_set, total = build_query_to_datatable(
        query_set,
        search_query["asorting_cols"],
        search_query["custom_search"],
        search_query["searchable_columns"],
        search_query["start_record"],
        search_query["end_record"]
    )

    obj_map = dict()
    obj_map['query_set'] = query_set
    obj_map["total"] = total

    obj_map["next_search"] = search_query.copy()
    obj_map["next_search"]["start_record"] += 25
    obj_map["next_search"]["end_record"] += 25

    obj_map["prev_search"] = None
    if search_query["start_record"] > 0:
        t = search_query["end_record"] - search_query["start_record"]
        i = t - 25
        f = search_query["start_record"]
        obj_map["prev_search"] = search_query.copy()
        obj_map["prev_search"]["start_record"] = i if i >= 0 else 0
        obj_map["prev_search"]["end_record"] = f if f >= 0 else 25

    return obj_map
