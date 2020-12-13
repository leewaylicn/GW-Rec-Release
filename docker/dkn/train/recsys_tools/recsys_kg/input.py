# import tensorflow as tf
import json
import numpy as np

click_entities = np.arange(480).reshape([30,16])

click_words = np.arange(480).reshape([30,16])

news_entities = np.arange(16)

news_words = np.arange(16)

instance = {
    "click_entities": click_entities.tolist(),
    "click_words": click_words.tolist(),
    "news_entities": news_entities.tolist(),
    "news_words": news_words.tolist()
}

data = json.dumps({"signature_name": "serving_default", "instances": [instance,instance]})
print('Data: {} ... {}'.format(data[:50], data[len(data) - 52:]))

import requests

headers = {"content-type": "application/json"}
json_response = requests.post('http://18.179.53.40/v1/models/dkn:predict', data=data, headers=headers)
print(json_response.text)
predictions = json.loads(json_response.text)['predictions']
print(predictions)