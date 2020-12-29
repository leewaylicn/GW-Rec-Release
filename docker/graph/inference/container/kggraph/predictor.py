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

@app.route('/invocations', methods=['POST'])
def transformation():
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
        predictions=[]
        for d in data:
            predictions.append(ScoringService.predict(data))
        rr = json.dumps({'result': np.asarray(predictions).tolist()})
        print("bytes prediction is {}".format(rr))
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
