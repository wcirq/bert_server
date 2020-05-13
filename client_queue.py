# -*- coding: utf-8 -*- 
# @Time 2020/5/12 10:00
# @Author wcy
import time
import uuid

import numpy as np
import grpc
from queue import Queue
import grpc_base.bert_server_queue_pb2 as bert_server_queue_pb2
import grpc_base.bert_server_queue_pb2_grpc as bert_server_queue_pb2_grpc
import threading

sentence_queue = Queue(maxsize=32)


def generate():
    global sentence_queue
    while True:
        sentence = sentence_queue.get()
        time.sleep(0.9)
        yield sentence


def add():
    global sentence_queue
    text = ["我在这里"]
    while True:
        scale = np.random.randint(1, 3, (1,))[0]
        token = uuid.uuid1().hex
        texts = bert_server_queue_pb2.Texts(token=token, sentences=text * scale)
        sentence_queue.put(texts)
        time.sleep(0.001)


def run():
    # 连接 rpc 服务器
    # channel = grpc.insecure_channel('localhost:50051')
    channel = grpc.insecure_channel('172.16.204.14:50051')
    # 调用 rpc 服务
    stub = bert_server_queue_pb2_grpc.BertServetStub(channel)

    t = threading.Thread(target=add)
    t.setDaemon(True)
    t.start()

    response = stub.get_vectors(generate())
    for reply_vectors in response:
        reply = reply_vectors.reply
        for vectors in reply:
            token = vectors.token
            vectors = vectors.vectors
            vectors = np.array([list(v.vector) for v in vectors])
            print()

    # response = stub.get_vector(bert_server_pb2.Text(sentence="我在这里"))
    # print(response.vector)


if __name__ == '__main__':
    run()
