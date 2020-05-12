# -*- coding: utf-8 -*- 
# @Time 2020/5/12 10:00
# @Author wcy

# -*- coding: utf-8 -*-
# @Time 2020/5/12 9:48
# @Author wcy

from concurrent import futures
import numpy as np
import time
import grpc
from common.config import logger
from bert.bert2vec import BertEncode
from grpc_base import bert_server_pb2, bert_server_pb2_grpc


# 实现 proto 文件中定义的 BertServetServicer
class Greeter(bert_server_pb2_grpc.BertServetServicer):

    def __init__(self):
        super().__init__()
        self.text2vec = BertEncode(graph_path=None)
        logger.info("\033[1;32mbert initialize ok\033[0m")

    def get_vectors(self, request, context):
        vectors = self.text2vec.encode(request.sentences)
        vectors = [bert_server_pb2.Vector(vector=vector) for vector in vectors]
        vectors = bert_server_pb2.Vectors(vectors=vectors)
        return vectors

    def get_vector(self, request, context):
        vector = self.text2vec.encode(request.sentence)[0]
        vector = bert_server_pb2.Vector(vector=vector)
        return vector


def serve():
    # 启动 rpc 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bert_server_pb2_grpc.add_BertServetServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(60 * 60 * 24)  # one day in seconds
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
