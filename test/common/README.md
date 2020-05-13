# 构建gRPC步骤的例子  
 
###1.安装python包:
```shell script
pip install grpcio-tools grpcio
```
###2.编译 proto 文件  
```shell script
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. helloworld.proto
```
##### 解释
- python -m grpc_tools.protoc: python 下的 protoc 编译器通过 python 模块(module) 实现
- --python_out=. : 编译生成处理 protobuf 相关的代码的路径, 这里生成到当前目录
- --grpc_python_out=. : 编译生成处理 grpc 相关的代码的路径, 这里生成到当前目录
- -I. helloworld.proto : proto 文件的路径, 这里的 proto 文件在当前目录
##### 编译后生成的代码:
* helloworld_pb2.py: 用来和 protobuf 数据进行交互
* helloworld_pb2_grpc.py: 用来和 grpc 进行交互
###3.编写 helloworld 的 grpc 实现:
- 服务器端: helloworld_grpc_server.py
- 客户端: helloworld_grpc_client.py