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

import requests
from requests.adapters import HTTPAdapter

import redis

graph_url = os.environ['GRAPH_URL']
dkn_url = os.environ['DKN_URL']

graph_url="http://"+graph_url+"/invocations"
dkn_url="http://"+dkn_url+"/v1/models/dkn:predict"

print("GRAPH_URL: %s" % graph_url)
print("DKN_URL: %s" % dkn_url)

redis_url = os.environ['REDIS_URL']
redis_port = int(os.environ['REDIS_PORT'])

# The flask app for serving predictions
app = flask.Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    # health = ScoringService.get_model() is not None  # You can insert a health check here

    # status = 200 if health else 404
    status = 200
    return flask.Response(response='\n',
                          status=status,
                          mimetype='application/json')


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
        #data = data['instance']
        print("final data is {}".format(data))
        #s = StringIO(data)
        #print("test!! recieve text is {}".format(s))
        #data = s
        # data = pd.read_csv(s, header=None)
    else:
        return flask.Response(response='This predictor only supports CSV data',
                              status=415,
                              mimetype='text/plain')

    # print('Invoked with {} records'.format(data.shape[0]))
    '''
    input：
    {
        “recall”:[{“id”:1234,”title”:”中国银行”},{“id”:3434,”title”:”中兴进入美国市场”}],
        “history”:[{“id”:5555,”title”:”中国银行收紧银根”},{“id”:3334,”title”:”股市低迷”}],
        "userid":1234
    }
    output:
    {
    “result”:[{“id”:5555,”score”:0.23},{“id”:3334,”score”:0.11}]
    }
    '''
    #
    # 0.0 init (request session, and set retries to 3
    #
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))

    userid = data['userid']

    #
    # 0.1 exception process for 1 recall, return by 1 directly
    #      
    if len(data['recall']) == 1:
        dict = {}
        dict[data['recall'][0]["id"]] = 1.0

        r = redis.StrictRedis(host=redis_url, port=redis_port, db=0)
        result = r.zadd(userid, dict)
        print("set to redis ",result)

        results = []
        result = {
            "id": data['recall'][0]["id"],
            "score": 1
        }
        results.append(result)

        response = {"result": results}
        return flask.Response(response=json.dumps(response), status=200, mimetype='application/json')

    #
    # 1.1 build history info graph vector
    #
    history = []
    for i in data['history']:
        print(i['title'])
        history.append(i['title'])
    print(history)

    #
    # 1.2 post history info graph vector
    #
    #graph_url = 'http://54.87.130.9:8080/invocations'  #history urll ???
    header = {'Content-Type': 'application/json'}
    his_data = {"instance": history}
    his_res = s.post(graph_url, data=json.dumps(his_data), headers=header, timeout=5)
    print(his_res.text)

    #
    # 2.1 build recall info graph vector
    #  
    recall = []
    for i in data['recall']:
        print(i['title'])
        recall.append(i['title'])
    print(recall)

    #
    # 2.2 post recall info graph vector
    #    
    #graph_url=graph_url='http://54.87.130.9:8080/invocations' #recall urll ???
    header = {'Content-Type': 'application/json'}
    recall_data = {"instance": recall}
    recall_res = s.post(
        graph_url, 
        data=json.dumps(recall_data), 
        headers=header,
        timeout=10
    )
    print(recall_res.text)

    #
    # 3.1 build click_entities
    #  
    his_res_data=json.loads(his_res.text)
    #build click_entities
    click_entities = []
    for i in his_res_data['result']:
        tmp=list(map(lambda x: x > 6729 and 6729 or x, i[1]))
        click_entities.append(tmp)
    for j in range(0,30-len(his_res_data['result'])):
        click_entities.append([0]*16)

    print(click_entities)

    #
    # 3.2 build click_words
    #  
    click_words = []
    for i in his_res_data['result']:
        tmp=list(map(lambda x: x > 10061 and 10061 or x, i[0]))
        click_words.append(tmp)
    for j in range(0,30-len(his_res_data['result'])):
        click_words.append([0]*16)        
    print(click_words)

    #
    # 3.3 build full vector with news_words/news_entities/click_words/click_entities
    #  
    instances = []
    for i in json.loads(recall_res.text)['result']:
        news_words=list(map(lambda x: x > 10061 and 10061 or x, i[0]))
        news_entities=list(map(lambda x: x > 6729 and 6729 or x, i[1]))
        #news_words = i[0]
        #news_entities = i[1]
        instance = {
            "news_words": news_words,
            "news_entities": news_entities,
            "click_words": click_words,
            "click_entities": click_entities
        }
        instances.append(instance)
    dkn_data = {"signature_name": "serving_default", "instances": instances}
    print(dkn_data)

    #
    # 3.4 build full vector with news_words/news_entities/click_words/click_entities
    # 
    #dkn_url='https://api.ireaderm.net/account/charge/info/android' #dkn urll ???
    header = {'Content-Type': 'application/json'}
    dkn_res = requests.post(dkn_url, 
        data=json.dumps(dkn_data), 
        headers=header, 
        timeout=3
    )
    print(dkn_res.text)

    #
    # 4.1 process results of dkn
    # 
    dict = {}
    tmp = json.loads(dkn_res.text)
    for i in range(len(data['recall'])):
        dict[data['recall'][i]["id"]] = tmp['predictions'][i]

    #
    # 4.2 set to redis
    # 
    r=redis.StrictRedis(host=redis_url,port=redis_port,db=0)
    result=r.zadd(userid,dict)
    print("set to redis ",result)

    #
    # 4.3 repsonse to http caller
    # 
    '''
    response = {"result": result}
    return flask.Response(response=json.dumps(response), status=200, mimetype='application/json')
    '''

    results = []
    tmp = json.loads(dkn_res.text)
    for i in range(len(data['recall'])):
        result = {
            "id": data['recall'][i]["id"],
            "score": tmp['predictions'][i]
        }
        results.append(result)
    response = {"result": results}

    return flask.Response(response=json.dumps(response), status=200, mimetype='application/json')

