# -*- coding: utf-8 -*- 
# @Time 2020/5/6 15:17
# @Author wcy
import json
import os
import time
import sys
import numpy as np
import tensorflow as tf
sys.path.append("../../")

from bert import tokenization, args, modeling


def bert_init():
    # we don't need GPU for optimizing the graph
    from tensorflow.python.tools.optimize_for_inference_lib import optimize_for_inference
    tf.gfile.MakeDirs(args.output_dir)

    config_fp = args.config_name

    # 加载bert配置文件
    with tf.gfile.GFile(config_fp, 'r') as f:
        bert_config = modeling.BertConfig.from_dict(json.load(f))

    input_ids = tf.placeholder(tf.int32, (None, None), 'input_ids')
    input_mask = tf.placeholder(tf.int32, (None, None), 'input_mask')
    input_type_ids = tf.placeholder(tf.int32, (None, None), 'input_type_ids')

    jit_scope = tf.contrib.compiler.jit.experimental_jit_scope

    with jit_scope():
        input_tensors = [input_ids, input_mask, input_type_ids]

        model = modeling.BertModel(
            config=bert_config,
            is_training=False,
            input_ids=input_ids,
            input_mask=input_mask,
            token_type_ids=input_type_ids,
            use_one_hot_embeddings=False)

        # 获取所有要训练的变量
        tvars = tf.trainable_variables()

        init_checkpoint = args.ckpt_name
        (assignment_map, initialized_variable_names) = modeling.get_assignment_map_from_checkpoint(tvars,
                                                                                                   init_checkpoint)

        tf.train.init_from_checkpoint(init_checkpoint, assignment_map)

        # 共享卷积核
        with tf.variable_scope("pooling"):
            # 如果只有一层，就只取对应那一层的weight
            if len(args.layer_indexes) == 1:
                encoder_layer = model.all_encoder_layers[args.layer_indexes[0]]
            else:
                # 否则遍历需要取的层，把所有层的weight取出来并拼接起来shape:768*层数
                all_layers = [model.all_encoder_layers[l] for l in args.layer_indexes]
                encoder_layer = tf.concat(all_layers, -1)

        mul_mask = lambda x, m: x * tf.expand_dims(m, axis=-1)
        masked_reduce_mean = lambda x, m: tf.reduce_sum(mul_mask(x, m), axis=1) / (
                tf.reduce_sum(m, axis=1, keepdims=True) + 1e-10)

        input_mask = tf.cast(input_mask, tf.float32)
        # 以下代码是句向量的生成方法，可以理解为做了一个卷积的操作，但是没有把结果相加, 卷积核是input_mask
        pooled = masked_reduce_mean(encoder_layer, input_mask)
        pooled = tf.identity(pooled, 'final_encodes')

        output_tensors = [pooled]
        tmp_g = tf.get_default_graph().as_graph_def()

    # allow_soft_placement:自动选择运行设备
    config = tf.ConfigProto(allow_soft_placement=True)
    with tf.Session(config=config) as sess:
        sess.run(tf.global_variables_initializer())
        tmp_g = tf.graph_util.convert_variables_to_constants(sess, tmp_g, [n.name[:-2] for n in output_tensors])
        dtypes = [n.dtype for n in input_tensors]
        tmp_g = optimize_for_inference(
            tmp_g,
            [n.name[:-2] for n in input_tensors],
            [n.name[:-2] for n in output_tensors],
            [dtype.as_datatype_enum for dtype in dtypes],
            False)
    temp_file = os.path.join(args.output_dir, args.pb_file)
    with tf.gfile.GFile(temp_file, 'wb') as f:
        f.write(tmp_g.SerializeToString())
    return temp_file


class BertEncode(object):

    def __init__(self, max_seq_len=45, graph_path=None):
        if graph_path is None:
            graph_path = os.path.join(args.output_dir, args.pb_file)
        self.max_seq_len = max_seq_len
        self.tokenizer = tokenization.FullTokenizer(vocab_file=args.vocab_file, do_lower_case=True)
        if not os.path.exists(graph_path):
            graph_path = bert_init()

        self.input_ids = tf.placeholder(tf.int32, (None, max_seq_len), 'input_ids')
        self.input_mask = tf.placeholder(tf.int32, (None, max_seq_len), 'input_mask')
        self.input_type_ids = tf.placeholder(tf.int32, (None, max_seq_len), 'input_type_ids')
        with tf.gfile.GFile(graph_path, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())

        self.output = tf.import_graph_def(graph_def,
                                          input_map={'input_ids:0': self.input_ids,
                                                     'input_mask:0': self.input_mask,
                                                     'input_type_ids:0': self.input_type_ids},
                                          return_elements=['final_encodes:0'])
        self.sess = tf.Session()
        # 初始化Session
        temp = np.zeros((1, self.max_seq_len), np.int)
        temp_feed_dict = {self.input_ids: temp, self.input_mask: temp, self.input_type_ids: temp}
        self.sess.run(self.output, feed_dict=temp_feed_dict)

    def deal_text(self, texts):
        input_ids = []
        input_masks = []
        input_type_ids = []

        for text in texts:
            tokens = []
            input_type_id = []
            text_list = self.tokenizer.tokenize(text)
            if len(text_list) > self.max_seq_len - 2:
                text_list = text_list[0:(self.max_seq_len - 2)]
            tokens.append("[CLS]")
            input_type_id.append(0)
            for token in text_list:
                tokens.append(token)
                input_type_id.append(0)
            tokens.append("[SEP]")
            input_type_id.append(0)

            input_id = self.tokenizer.convert_tokens_to_ids(tokens)

            input_mask = [1] * len(input_id)
            while len(input_id) < self.max_seq_len:
                input_id.append(0)
                input_mask.append(0)
                input_type_id.append(0)
            input_ids.append(input_id)
            input_masks.append(input_mask)
            input_type_ids.append(input_type_id)
        return input_ids, input_masks, input_type_ids

    def encode(self, sentences: [str, list]):
        if isinstance(sentences, str):
            sentences = [sentences]
        input_ids, input_masks, input_type_ids = self.deal_text(sentences)
        output = self.sess.run(self.output, feed_dict={
            self.input_ids: input_ids,
            self.input_mask: input_masks,
            self.input_type_ids: input_type_ids
        })
        return output[0]


if __name__ == '__main__':
    text2vec = BertEncode(graph_path=None)
    while 1:
        text = ["我在这里"]*100
        res1 = text2vec.encode(text)
        for i in range(10):
            s = time.time()
            for j in range(1):
                res1 = text2vec.encode(text)
            e = time.time()
            print(f"time{len(text)}: {(e- s)/1}")
            text = text * 2
        print()
