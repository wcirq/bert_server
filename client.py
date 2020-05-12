# -*- coding: utf-8 -*- 
# @Time 2020/5/12 10:00
# @Author wcy
import numpy as np
import grpc
import grpc_base.bert_server_pb2 as bert_server_pb2
import grpc_base.bert_server_pb2_grpc as bert_server_pb2_grpc

def run():
    # 连接 rpc 服务器
    channel = grpc.insecure_channel('localhost:50051')
    # 调用 rpc 服务
    stub = bert_server_pb2_grpc.BertServetStub(channel)
    response = stub.get_vectors(bert_server_pb2.Texts(sentences=["我在这里", "你好啊"]))
    vectors = np.array([list(v.vector) for v in response.vectors])
    print(vectors)
    response = stub.get_vector(bert_server_pb2.Text(sentence="我在这里"))
    print(response.vector)


if __name__ == '__main__':
    run()