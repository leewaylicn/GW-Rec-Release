import json

data = {
  "recall": [{"id": "gsxw-3528874", "title": [[[21, 327, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [281469, 281469, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]]}],
  "history": [{"id": 1234, "title": [[[21, 327, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [281469, 281469, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]]}, {"id": "gsxw-3528874", "title": [[[21, 327, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [281469, 281469, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]]}],
  "usedid": "1545128ada"
}

history_num = 30
title_len = 16

input_data = {}

input_data['news_words'] = data['recall'][0]['title'][0][0]
input_data['news_entities'] = data['recall'][0]['title'][0][1]
input_data['click_words'] = [[0]*title_len for row in range(history_num)]
input_data['click_entities'] = [[0]*title_len for row in range(history_num)]

for cn, hist in enumerate(data['history']):
    input_data['click_words'][cn] = hist['title'][0][0]
    input_data['click_entities'][cn] = hist['title'][0][1]

print(input_data)