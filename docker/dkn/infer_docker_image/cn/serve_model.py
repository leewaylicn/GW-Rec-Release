import boto3, sys

## python copy_model.py s3://leigh-gw/dkn_model/dkn-2020-11-28-06-41-17-782/output/model.tar.gz ./
model_dir = '/opt/ml/model/dkn/'
s3client = boto3.client('s3')

# 通过环境变量获取 model S3位置，并且下载
import os

model_s3_key = os.getenv('MODEL_S3_KEY')
print("model key is {}".format(model_s3_key))

bucket, key = model_s3_key.split('/', 2)[-1].split('/', 1)
print("bucket is {}, key is {}".format(bucket,key))

s3client.download_file(bucket, key, model_dir + '/model.tar.gz')
print("model is located at {}, download succeed".format(model_s3_key))

# 解压缩
import tarfile


def extract(tar_path, target_path):
    tar = tarfile.open(tar_path, "r:gz")
    file_names = tar.getnames()
    for file_name in file_names:
        tar.extract(file_name, target_path)
    tar.close()


extract('/opt/ml/model/dkn/model.tar.gz', model_dir)
print('extract succeed')

# run model
print('serving model ...')
os.system('tensorflow_model_server --port=8500 --rest_api_port=8501 --model_name=dkn --model_base_path=/opt/ml/model/dkn')
