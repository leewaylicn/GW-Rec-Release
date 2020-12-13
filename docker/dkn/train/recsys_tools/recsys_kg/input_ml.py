import json
import numpy as np

click_entities = np.arange(1)

click_words = np.arange(1)

news_entities = np.arange(1)

news_words = np.arange(1)

instance = {
    "age": click_entities.tolist(),
    "gender": click_words.tolist(),
    "movie_id": news_entities.tolist(),
    "occupation": news_words.tolist()
}

data = json.dumps({"signature_name": "serving_default", "instances": [instance]})

import requests

headers = {"content-type": "application/json"}
json_response = requests.post('http://18.180.157.88/v1/models/ml-deepFM:predict', data=data, headers=headers)
print(data)
print(json_response.text)
predictions = json.loads(json_response.text)['predictions']
print(predictions)
