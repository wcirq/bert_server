# -*- coding: utf-8 -*- 
# @Time 2020/5/13 15:04
# @Author wcy

import grpc
import random

from test.flow import routeguide_pb2, routeguide_pb2_grpc, routeguide_db


def get_feature(feature):
    if not feature.location:
        print("Server returned incomplete feature")
        return
    if feature.name:
        print("Feature called {name} at {location}".format(name = feature.name, location = feature.location))
    else:
        print("Found no feature at {location}".format(location = feature.location))

def generate_route(feature_list):
    for _ in range(0, 20):
        random_feature = feature_list[random.randint(0, len(feature_list) - 1)]
        print("random feature {name} at {location}".format(
            name=random_feature.name, location=random_feature.location))
        yield random_feature.location

def make_route_note(message, latitude, longitude):
    return routeguide_pb2.RouteNote(
        message=message,
        location=routeguide_pb2.Point(latitude=latitude, longitude=longitude))

def generate_route_note():
    msgs = [
        make_route_note('msg 1', 0, 0),
        make_route_note('msg 2', 1, 0),
        make_route_note('msg 3', 0, 1),
        make_route_note('msg 4', 0, 0),
        make_route_note('msg 5', 1, 1),
    ]
    for msg in msgs:
        print("send message {message} location {location}".format(message = msg.message, location = msg.location))
        yield msg


def run():
    channel = grpc.insecure_channel('172.16.204.14:50051')
    stub = routeguide_pb2_grpc.RouteGuideStub(channel)
    print("\033[1;32m-------------- GetFeature 客服端一次请求, 服务器一次应答 --------------\033[0m")
    response = stub.GetFeature(routeguide_pb2.Point(latitude=409146138, longitude=-746188906))
    get_feature(response)
    response = stub.GetFeature(routeguide_pb2.Point(latitude=0, longitude=-0))
    get_feature(response)

    print("\033[1;32m-------------- ListFeatures 客服端一次请求, 服务器多次应答(流式) --------------\033[0m")
    response = stub.ListFeature(routeguide_pb2.Rectangle(
        lo = routeguide_pb2.Point(latitude=400000000, longitude=-750000000),
        hi=routeguide_pb2.Point(latitude=420000000, longitude=-730000000)
    ))
    for feature in response:
        print("Feature called {name} at {location}".format(name=feature.name, location=feature.location))

    print("\033[1;32m-------------- RecordRoute 客服端多次请求(流式), 服务器一次应答 --------------\033[0m")
    feature_list = routeguide_db.read_routeguide_db()
    route_iterator = generate_route(feature_list)
    response = stub.RecordRoute(route_iterator)
    print("point count: {point_count} feature count: {feature_count} distance: {distance} elapsed time:{elapsed_time}".format(
        point_count  = response.point_count,
        feature_count = response.feature_count,
        distance = response.distance,
        elapsed_time = response.elapsed_time
    ))

    print("\033[1;32m-------------- RouteChat 客服端多次请求(流式), 服务器多次应答(流式) --------------\033[0m")
    response = stub.RouteChat(generate_route_note())
    for msg in response:
        print("recived message {message} location {location}".format(
            message=msg.message, location=msg.location))


if __name__ == '__main__':
    run()