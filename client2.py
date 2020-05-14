# -*- coding: utf-8 -*- 
# @Time 2020/5/12 10:00
# @Author wcy
import time
import threading
import numpy as np
import grpc
from tqdm import tqdm
import grpc_base.bert_server_pb2 as bert_server_pb2
import grpc_base.bert_server_pb2_grpc as bert_server_pb2_grpc


def predict(stub, text):
    # s = time.time()
    response = stub.get_vectors(bert_server_pb2.Texts(sentences=text))
    vectors = np.array([list(v.vector) for v in response.vectors])
    # e = time.time()
    # print(len(vectors), e-s)


def batch_predict(n=1000):
    # 连接 rpc 服务器
    # channel = grpc.insecure_channel('localhost:50051')
    channel = grpc.insecure_channel('172.16.204.14:50051')
    # 调用 rpc 服务
    stub = bert_server_pb2_grpc.BertServetStub(channel)
    text = ["我在这里"]
    ts = []
    s = time.time()
    for i in tqdm(range(n), mininterval=10):
        # predict(stub, text)
        t = threading.Thread(target=predict, args=(stub, text))
        t.setDaemon(True)
        ts.append(t)
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    e = time.time()
    print(f"batch predict {n} time: {e - s}")


def single_predict(n=1000):
    # 连接 rpc 服务器
    # channel = grpc.insecure_channel('localhost:50051')
    channel = grpc.insecure_channel('172.16.204.14:50051')
    # 调用 rpc 服务
    stub = bert_server_pb2_grpc.BertServetStub(channel)
    text = ["我在这里"]*600
    s = time.time()
    for i in tqdm(range(n)):
        predict(stub, text)
    e = time.time()
    print(f"single predict {n} time: {e - s}")


def run():
    # batch_predict(n=2000)
    single_predict(n=1)


if __name__ == '__main__':
    run()