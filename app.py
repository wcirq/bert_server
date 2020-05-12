# -*- coding: utf-8 -*- 
# @Time 2020/5/12 12:54
# @Author wcy
import os
import platform
from flask import Flask, request, jsonify, json
from bert.bert2vec import BertEncode
import sys

from common.config import logger

sys.path.append("../../")
sys = platform.system()
if sys == "Linux":
    # 自动选择空闲显卡
    os.system('nvidia-smi -q -d Memory |grep -A4 GPU|grep Free >tmp')
    memory_gpu = [int(x.split()[2]) for x in open('tmp', 'r').readlines()]
    gpu_id = memory_gpu.index(max(memory_gpu))
    os.environ["CUDA_VISIBLE_DEVICES"] = f"{gpu_id}"
    logger.info(f"\033[1;32m使用{gpu_id}号gpu\033[0m")

app = Flask(__name__)
text2vec = BertEncode(graph_path=None)


def flask_content_type(requests):
    """根据不同的content_type来解析数据"""
    if requests.method == 'POST':
        if requests.content_type == 'application/x-www-form-urlencoded':
            data = requests.form
        elif requests.content_type == 'application/json':
            data = requests.json
        else:  # 无法被解析出来的数据
            data = json.loads(requests.data)
        return data
    elif requests.method == 'GET':
        return requests.args


@app.route('/get_vectors', methods=['POST'])
def get_vectors():
    datas = flask_content_type(request)
    vectors = text2vec.encode(datas["sentences"])
    return jsonify(code=0, message="", data=vectors.tolist())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50051)