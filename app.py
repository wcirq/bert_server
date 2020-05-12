# -*- coding: utf-8 -*- 
# @Time 2020/5/12 12:54
# @Author wcy

from flask import Flask, request, jsonify, json

from bert.bert2vec import BertEncode

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