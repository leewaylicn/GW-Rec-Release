from __future__ import print_function

import os
import json
import pickle
from io import StringIO
import sys
import signal
import traceback
import numpy as np

import flask

import pandas as pd
import kg
import encoding

import redis

prefix = '/opt/ml/'
model_path = os.path.join(prefix, 'model')

kg_path = os.environ['GRAPH_BUCKET']
dbpedia_key = os.environ['KG_DBPEDIA_KEY']
entity_key = os.environ['KG_ENTITY_KEY']
relation_key = os.environ['KG_RELATION_KEY']
entity_industry_key = os.environ['KG_ENTITY_INDUSTRY_KEY']
vocab_key = os.environ['KG_VOCAB_KEY']
data_input_key = os.environ['DATA_INPUT_KEY']
train_output_key = os.environ['TRAIN_OUTPUT_KEY']
redis_url = os.environ['REDIS_URL']
redis_port = int(os.environ['REDIS_PORT'])
print(kg_path)
print(redis_url)
print(redis_port)

# graph = kg.Kg('kg')
# model = encoding.encoding(graph)

# A singleton for holding the model. This simply loads the model and holds it.
# It has a predict function that does a prediction based on the model and the input data.

class ScoringService(object):
    env = {
        'GRAPH_BUCKET': kg_path,
        'KG_DBPEDIA_KEY': dbpedia_key,
        'KG_ENTITY_KEY': entity_key,
        'KG_RELATION_KEY': relation_key,
        'KG_ENTITY_INDUSTRY_KEY': entity_industry_key,
        'KG_VOCAB_KEY': vocab_key,
        'DATA_INPUT_KEY': data_input_key,
        'TRAIN_OUTPUT_KEY': train_output_key
    }

    graph = kg.Kg(env) # Where we keep the model when it's loaded
    model = encoding.encoding(graph, env)

    @classmethod
    def get_model(cls):
        """Get the model object for this instance, loading it if it's not already loaded."""
        if cls.model == None:
            # import kg
            # import encoding
            cls.model = model
            # with open(os.path.join(model_path, 'decision-tree-model.pkl'), 'r') as inp:
            #     cls.model = pickle.load(inp)
        return cls.model

    @classmethod
    def predict(cls, input):
        """For the input, do the predictions and return them.

        Args:
            input (a pandas dataframe): The data on which to do the predictions. There will be
                one prediction per row in the dataframe"""
        clf = cls.get_model()
        return clf[input]

# The flask app for serving predictions
app = flask.Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    # health = ScoringService.get_model() is not None  # You can insert a health check here

    # status = 200 if health else 404
    status = 200
    return flask.Response(response='\n', status=status, mimetype='application/json')

@app.route('/batch', methods=['POST'])
def batch():
    """Do an inference on a single batch of data. In this sample server, we take data as CSV, convert
    it to a pandas data frame for internal use and then convert the predictions back to CSV (which really
    just means one prediction per line, since there's a single column.
    """
    data = None

    # Convert from CSV to pandas
    if flask.request.content_type == 'application/json':
        print("raw data is {}".format(flask.request.data))
        data = flask.request.data.decode('utf-8')
        print("data is {}".format(data))
        data = json.loads(data)
        data = data['instance']
        print("final data is {}".format(data))
        #s = StringIO(data)
        #print("test!! recieve text is {}".format(s))
        #data = s
        # data = pd.read_csv(s, header=None)
    else:
        return flask.Response(response='This predictor only supports CSV data', status=415, mimetype='text/plain')

    # print('Invoked with {} records'.format(data.shape[0]))

    # Do the prediction
    predictions=[]
    for d in data:
        predictions.append(ScoringService.predict(data))
    # print("prediction is {}".format(predictions))

    ## Convert from numpy back to CSV
    #out = StringIO.StringIO()
    #pd.DataFrame({'results':predictions}).to_csv(out, header=False, index=False)
    #result = out.getvalue()
    rr = json.dumps({'result': np.asarray(predictions).tolist()})
    print("bytes prediction is {}".format(rr))

    return flask.Response(response=rr, status=200, mimetype='application/json')

@app.route('/invocations', methods=['POST'])
def invocations():
    """Do an inference on a single batch of data. In this sample server, we take data as CSV, convert
    it to a pandas data frame for internal use and then convert the predictions back to CSV (which really
    just means one prediction per line, since there's a single column.
    """
    data = None

    # Convert from CSV to pandas
    if flask.request.content_type == 'application/json':
        print("raw data is {}".format(flask.request.data))
        data = flask.request.data.decode('utf-8')
        print("data is {}".format(data))
        data = json.loads(data)
        title = data['title']#.encode('utf-8')
        userid = data['id']
        print("final data is {}".format(data))
    else:
        return flask.Response(response='This predictor only supports CSV data', status=415, mimetype='text/plain')

    # Do the prediction
    predictions=[]
    predictions.append(ScoringService.predict(title))
    print(predictions)
    print(json.dumps(np.asarray(predictions).tolist()))

    r=redis.StrictRedis(host=redis_url,port=redis_port,db=0)
    result=r.set(userid, json.dumps(np.asarray(predictions).tolist()), ex=86400*30)    

    rr = json.dumps({'result': np.asarray(predictions).tolist()})
    print("bytes prediction is {}".format(rr))

    return flask.Response(response=rr, status=200, mimetype='application/json')