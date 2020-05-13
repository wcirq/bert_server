# -*- coding: utf-8 -*- 
# @Time 2020/5/12 10:00
# @Author wcy
import time

import numpy as np
import grpc
import grpc_base.bert_server_pb2 as bert_server_pb2
import grpc_base.bert_server_pb2_grpc as bert_server_pb2_grpc


def run():
    # 连接 rpc 服务器
    # channel = grpc.insecure_channel('localhost:50051')
    channel = grpc.insecure_channel('172.16.204.14:50051')
    # 调用 rpc 服务
    stub = bert_server_pb2_grpc.BertServetStub(channel)
    text = ["我在这里"]
    for i in range(10):
        s = time.time()
        for i in range(1):
            response = stub.get_vectors(bert_server_pb2.Texts(sentences=text))
            vectors = np.array([list(v.vector) for v in response.vectors])
        e = time.time()
        print(f"time{len(vectors)}: {int((e-s)/1*1000)} \n ")
        text *= 2
    # response = stub.get_vector(bert_server_pb2.Text(sentence="我在这里"))
    # print(response.vector)


if __name__ == '__main__':
    run()