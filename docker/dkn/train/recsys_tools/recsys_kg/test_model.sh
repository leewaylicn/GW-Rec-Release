docker run --rm -p 80:8501 --mount type=bind,source=/home/ec2-user/GW,target=/home/ec2-user/GW -e MODEL_BASE_PATH=/home/ec2-user/GW/model_dir -e MODEL_NAME=dkn -t tensorflow/serving:latest

saved_model_cli show --dir dkn/1605324067/ --tag_set=serve --signature_def=serving_default
The given SavedModel SignatureDef contains the following input(s):
  inputs['click_entities'] tensor_info:
      dtype: DT_INT32
      shape: (-1, 30, 16)
      name: click_entities:0
  inputs['click_words'] tensor_info:
      dtype: DT_INT32
      shape: (-1, 30, 16)
      name: click_words:0
  inputs['news_entities'] tensor_info:
      dtype: DT_INT32
      shape: (-1, 16)
      name: news_entities:0
  inputs['news_words'] tensor_info:
      dtype: DT_INT32
      shape: (-1, 16)
      name: news_words:0
The given SavedModel SignatureDef contains the following output(s):
  outputs['prob'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1)
      name: Sigmoid:0
Method name is: tensorflow/serving/predict


saved_model_cli show --tag_set serve --signature_def serving_default --dir ml-deepFM/1/
The given SavedModel SignatureDef contains the following input(s):
  inputs['age'] tensor_info:
      dtype: DT_INT32
      shape: (-1, 1)
      name: serving_default_age:0
  inputs['gender'] tensor_info:
      dtype: DT_INT32
      shape: (-1, 1)
      name: serving_default_gender:0
  inputs['movie_id'] tensor_info:
      dtype: DT_INT32
      shape: (-1, 1)
      name: serving_default_movie_id:0
  inputs['occupation'] tensor_info:
      dtype: DT_INT32
      shape: (-1, 1)
      name: serving_default_occupation:0
The given SavedModel SignatureDef contains the following output(s):
  outputs['prediction_layer'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 1)
      name: StatefulPartitionedCall:0
Method name is: tensorflow/serving/predict