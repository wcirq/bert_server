# -*- coding: utf-8 -*- 
# @Time 2020/5/12 13:01
# @Author wcy
import time

import requests
from flask import json


def get_vectors(texts):
    # url = "http://127.0.0.1:50052/get_vectors"
    url = "http://172.16.204.14:50052/get_vectors"
    param = {
        "sentences": texts,
    }

    r = requests.post(url, data=json.dumps(param))
    reslus = r.json()


if __name__ == '__main__':
    text = ["我在这里"]
    for i in range(10):
        s = time.time()
        for i in range(5):
            response = get_vectors(text)
        e = time.time()
        print(f"time{len(text)}: {int((e - s) / 5 * 1000)} \n ")
        text *= 2