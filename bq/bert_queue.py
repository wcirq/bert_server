# -*- coding: utf-8 -*- 
# @Time 2020/5/14 10:05
# @Author wcy
import time
import uuid
import threading
import numpy as np
import pandas as pd
from queue import Queue, Empty
from bert.bert2vec import BertEncode
from common.config import logger


class Respect(object):

    def __init__(self, token, values):
        self.token = token
        self.values = values


class BertQueue(object):
    output_queue = {}

    def __init__(self, maxsize=32):
        self.input_queue = Queue(maxsize=maxsize)
        self.text2vec = BertEncode(graph_path=None)
        t = threading.Thread(target=self.run)
        t.setDaemon(True)
        t.start()
        logger.info("\033[1;32mbert initialize ok\033[0m")

    def put(self, sentences):
        token = uuid.uuid1().hex
        self.input_queue.put(Respect(token=token, values=sentences))
        return token

    def get(self, token):
        while True:
            if token in self.output_queue.keys():
                result = self.output_queue.pop(token)
                return result
            time.sleep(0.005)

    def run(self):
        inputs = []
        tokens = []
        start = time.time()
        while True:
            try:
                respect = self.input_queue.get(block=True, timeout=0.001)
                token = respect.token
                sentences = respect.values
                inputs.extend(sentences)
                tokens.extend([token] * len(sentences))
            except Empty as e:
                continue
            except Exception as e:
                logger.error(str(e))
                continue
            finally:
                end = time.time()
                interval = end - start
                if len(inputs) > 64 or (interval > 0.1 and len(inputs) > 0):
                    logger.info(f"batch size: {len(inputs)}, time: {interval}")
                    if len(inputs) > 512:
                        vectors = []
                        n = int(len(inputs) // 64) + 1
                        for i in range(n):
                            sentences = inputs[i * 64:(i + 1) * 64]
                            if len(sentences) == 0:
                                continue
                            vector = self.text2vec.encode(sentences)
                            vectors.append(vector)
                        vectors = np.concatenate(vectors, axis=0)
                    else:
                        vectors = self.text2vec.encode(inputs)
                    info = pd.DataFrame(np.array([tokens, inputs]).T, columns=["tokens", "inputs"]).groupby(
                        "tokens").indices
                    reply_vectors = {k: [vectors[i] for i in v] for k, v in info.items()}
                    self.output_queue.update(reply_vectors)
                    inputs = []
                    tokens = []
                    start = time.time()
