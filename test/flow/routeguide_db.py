# -*- coding: utf-8 -*- 
# @Time 2020/5/13 15:03
# @Author wcy

import json

from test.flow import routeguide_pb2


def read_routeguide_db():
    feature_list = []
    with open('route_guide_db.json') as f:
        for item in json.load(f):
            feature = routeguide_pb2.Feature(
                name = item['name'],
                location = routeguide_pb2.Point(
                    latitude=item['location']['latitude'],
                    longitude=item['location']['longitude']
                )
            )
            feature_list.append(feature)
    return feature_list