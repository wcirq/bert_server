# -*- coding: utf-8 -*- 
# @Time 2020/5/12 10:00
# @Author wcy
import os
import threading
from concurrent import futures
from queue import Queue

import numpy as np
import time
import grpc
from common.config import logger
from bert.bert2vec import BertEncode
from grpc_base import bert_server_pb2, bert_server_pb2_grpc
import platform
import sys

from bq.bert_queue import BertQueue

sys.path.append("../../")
sys = platform.system()
if sys == "Linux":
    # 自动选择空闲显卡
    os.system('nvidia-smi -q -d Memory |grep -A4 GPU|grep Free >tmp')
    memory_gpu = [int(x.split()[2]) for x in open('tmp', 'r').readlines()]
    gpu_id = memory_gpu.index(max(memory_gpu))
    os.environ["CUDA_VISIBLE_DEVICES"] = f"{gpu_id}"
    logger.info(f"\033[1;32m使用{gpu_id}号gpu\033[0m")


# 实现 proto 文件中定义的 BertServetServicer
class Greeter(bert_server_pb2_grpc.BertServetServicer):
    bert_queue = BertQueue(maxsize=32)

    def __init__(self):
        super().__init__()

    def get_vectors(self, request, context):
        token = self.bert_queue.put(request.sentences)
        reslut = self.bert_queue.get(token=token)
        if isinstance(reslut, dict):
            vectors = reslut.get(token, None)
            if vectors is None:
                return None
        vectors = reslut
        vectors = [bert_server_pb2.Vector(vector=vector) for vector in vectors]
        vectors = bert_server_pb2.Vectors(vectors=vectors)
        return vectors

    def get_vector(self, request, context):
        vector = self.bert_queue.text2vec.encode(request.sentence)[0]
        vector = bert_server_pb2.Vector(vector=vector)
        return vector


def serve():
    # 启动 rpc 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=64))
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
