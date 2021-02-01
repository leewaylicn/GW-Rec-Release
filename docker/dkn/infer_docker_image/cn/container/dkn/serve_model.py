from __future__ import print_function
import tarfile
import os
import boto3
import glob
import sys
import pandas as pd
import flask
import numpy as np
import traceback
import signal
import sys
from io import StringIO
import pickle
import json
from tensorflow.contrib import predictor

# python copy_model.py s3://leigh-gw/dkn_model/dkn-2020-11-28-06-41-17-782/output/model.tar.gz ./
model_dir = '/opt/ml/model/dkn/'
s3client = boto3.client('s3')

# 通过环境变量获取 model S3位置，并且下载

model_s3_key = os.getenv('MODEL_S3_KEY')
print("model key is {}".format(model_s3_key))

bucket, key = model_s3_key.split('/', 2)[-1].split('/', 1)
print("bucket is {}, key is {}".format(bucket, key))

s3client.download_file(bucket, key, model_dir + '/model.tar.gz')
print("model is located at {}, download succeed".format(model_s3_key))

# 解压缩

def extract(tar_path, target_path):
    tar = tarfile.open(tar_path, "r:gz")
    file_names = tar.getnames()
    for file_name in file_names:
        tar.extract(file_name, target_path)
    tar.close()

extract('/opt/ml/model/dkn/model.tar.gz', model_dir)
print('extract succeed')

# # run model
# print('serving model ...')
# os.system('tensorflow_model_server --port=8500 --rest_api_port=8501 --model_name=dkn --model_base_path=/opt/ml/model/dkn')
def check_parent_dir(current_parent, complete_dir):
    dir_split = complete_dir.split('/')
    if len(dir_split) == 1:
        if len(dir_split[0].split('.')) == 1:
            os.makedirs(os.path.join(current_parent,dir_split[0]))
        return
    else:
        if not os.path.exists(os.path.join(current_parent,dir_split[0])):
            os.makedirs(os.path.join(current_parent,dir_split[0]))
        check_parent_dir(os.path.join(current_parent,dir_split[0]), '/'.join(dir_split[1:]))

kg_folder = os.environ['GRAPH_BUCKET']
kg_entity_embed_key = os.environ['KG_ENTITY_EMBED_KEY']
kg_word_embed_key = os.environ['KG_WORD_EMBED_KEY']
kg_context_embed_key = os.environ['KG_CONTEXT_EMBED_KEY']

entity_embed = None
word_embed = None
context_embed = None

if not os.path.exists(kg_folder):
    os.makedirs(kg_folder)
if not os.path.exists(os.path.join(kg_folder, kg_entity_embed_key)):
    check_parent_dir('.', os.path.join(
        kg_folder, kg_entity_embed_key))
    s3client.download_file(kg_folder, kg_entity_embed_key, os.path.join(
        kg_folder, kg_entity_embed_key))
    entity_embed = np.load(os.path.join(
        kg_folder, kg_entity_embed_key))
    print("downloaded entity_embed")
if not os.path.exists(os.path.join(kg_folder, kg_word_embed_key)):
    check_parent_dir('.', os.path.join(
        kg_folder, kg_word_embed_key))
    s3client.download_file(kg_folder, kg_word_embed_key, os.path.join(
        kg_folder, kg_word_embed_key))
    word_embed = np.load(os.path.join(
        kg_folder, kg_word_embed_key))
    print("downloaded word_embed")
if not os.path.exists(os.path.join(kg_folder, kg_context_embed_key)):
    check_parent_dir('.', os.path.join(
        kg_folder, kg_context_embed_key))
    s3client.download_file(kg_folder, kg_context_embed_key, os.path.join(
        kg_folder, kg_context_embed_key))
    context_embed = np.load(os.path.join(
        kg_folder, kg_context_embed_key))
    print("downloaded context_embed")
class ScoringService(object):
    model = None

    @classmethod
    def get_model(cls):
        """Get the model object for this instance, loading it if it's not already loaded."""
        if cls.model == None:
            model_path = None
            for name in glob.glob(os.path.join(model_dir, '**', 'saved_model.pb'), recursive=True):
                print("found model saved_model.pb in {} !".format(name))
                model_path = '/'.join(name.split('/')[0:-1])
            
            cls.model = predictor.from_saved_model(model_path)
            print("load model succeed!")
            # with open(os.path.join(model_path, 'decision-tree-model.pkl'), 'r') as inp:
            #     cls.model = pickle.load(inp)
        return cls.model

    @classmethod
    def predict(cls, input_data):
        """For the input, do the predictions and return them."""
        model = cls.get_model()
        print("debug embedding!!!!!!")
        index = [range(16),range(16)]
        hist_index = [range(16),range(16),range(16),range(16),range(16),range(16),range(16),range(16),range(16),range(16),range(16),range(16),range(16),range(16),range(16),range(16)]
        # index_np = np.array(index)
        # hist_index_np = np.array(hist_index)

        news_words_index = []
        news_entity_index = []
        click_words_index = []
        click_entity_index = []

        # for d in input_data:
        #     print("type of d is {}".format(type(d['news_words'])))
        #     print("type of d[0] is {}".format(type(d['news_words'][0])))
        #     print("type of click d is {}".format(type(d['click_words'])))
        #     print("type of click d[0] is {}".format(type(d['click_words'][0])))
        #     print("type of click d[0][0] is {}".format(type(d['click_words'][0][0])))
        #     news_words_index.append(d['news_words'])
        #     news_entity_index.append(d['news_entities'])
        #     click_words_index = click_words_index + d['click_words']
        #     click_entity_index = click_entity_index + d['click_entities']
        
        news_words_index = index
        news_entity_index = index
        click_words_index = hist_index
        click_entity_index = hist_index
        

        news_words_index_np = np.array(news_words_index)
        news_entity_index_np = np.array(news_entity_index)
        for idx in news_words_index:
            print("news words len {} with array {}".format(len(idx), idx))
        for idx in news_entity_index:
            print("news entities len {} with array {}".format(len(idx), idx))
        for idx in click_entity_index:
            print("click entity len {} with array {}".format(len(idx), idx))
        for idx in click_words_index:
            print("click word len {} with array {}".format(len(idx), idx))
        click_words_index_np = np.array(click_words_index)
        click_entity_index_np = np.array(click_entity_index)

        input_dict = {}
        print(click_entity_index_np)
        input_dict['click_entities'] = entity_embed[click_entity_index_np]
        input_dict['click_words'] = word_embed[click_words_index_np]
        input_dict['news_entities'] = entity_embed[news_entity_index_np]
        input_dict['news_words'] = word_embed[news_words_index_np]

        output = model(input_dict)
        print("result is {}".format(output))
        return output

# The flask app for serving predictions
app = flask.Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    print("recieve ping")
    # health = ScoringService.get_model() is not None  # You can insert a health check here

    # status = 200 if health else 404
    status = 200
    return flask.Response(response='\n', status=status, mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def transformation():
    """Do an inference on a single batch of data. In this sample server, we take data as CSV, convert
    it to a pandas data frame for internal use and then convert the predictions back to CSV (which really
    just means one prediction per line, since there's a single column.
    """
    data = None

    # Convert from CSV to pandas
    if flask.request.content_type == 'application/json':
        # print("raw data is {}".format(flask.request.data))
        data = flask.request.data.decode('utf-8')
        # print("data is {}".format(data))
        data = json.loads(data)
        data = data['instance']
        # print("final data is {}".format(data))
        #s = StringIO(data)
        #print("test!! recieve text is {}".format(s))
        #data = s
        # data = pd.read_csv(s, header=None)
    elif flask.request.content_type == 'text/csv':
        print("batch transform raw data is {}".format(flask.request.data))
        data = flask.request.data.decode('utf-8')
        print("data is {}".format(data))
        s = StringIO(data)
        print("after StringIO {}".format(s))
        data = pd.read_csv(s, header=None, sep='\t')
        print("data frame is {}".format(data))
    else:
        return flask.Response(response='This predictor only supports application/json and text/csv data', status=415, mimetype='text/plain')

    # print('Invoked with {} records'.format(data.shape[0]))

    if flask.request.content_type == 'application/json':
        # Do the prediction
        predictions = []
        # for d in data:
        #     predictions.append(ScoringService.predict(data))
        predictions = ScoringService.predict(data)
        rr = json.dumps({'result': np.asarray(predictions['prob']).tolist()})
        # print("bytes prediction is {}".format(rr))
        return flask.Response(response=rr, status=200, mimetype='application/json')
    elif flask.request.content_type == 'text/csv':
        print('Invoked with {} records'.format(data.shape[0]))
        data_list = data.values.tolist()

        final_list = []
        for d in data_list:
            # Do the prediction
            result_list = []
            predictions = ScoringService.predict(d[2])
            print("prediction result is {}".format(predictions))
            word_index = predictions[0]
            entity_index = predictions[1]
            result_list.append(d[0])
            result_list.append(d[1])
            result_list.append(','.join([str(elem) for elem in word_index]))
            result_list.append(','.join([str(elem) for elem in entity_index]))
            final_list.append(result_list)

        out = StringIO()
        final_array = np.array(final_list)
        print("array {}".format(final_array))
        pd_dt = pd.DataFrame(final_array)
        print("dataframe is {}".format(pd_dt))
        pd_dt.to_csv(out, header=False, index=False)
        result = out.getvalue()
        print("result is {}".format(result))
        # # Convert from numpy back to CSV
        # out = StringIO.StringIO()
        # pd.DataFrame({'results':predictions}).to_csv(out, header=False, index=False)
        # result = out.getvalue()
        return flask.Response(response=result, status=200, mimetype='text/csv')
