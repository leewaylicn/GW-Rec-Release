import json
import os

import boto3

#from sagemaker.estimator import Estimator

from iam_helper import IamHelper
from sagemaker_controller import create_training_job, create_endpoint, \
    describe_training_job, describe_training_job_artifact, describe_endpoint, \
    list_endpoints

# bucket = os.environ['BUCKET']
# jobname = os.environ['JOB_NAME']
# instance = os.environ['INSTANCE']
# image_uri = os.environ['IMAGE_URI']
# task = os.environ['TASK']
_lambda = boto3.client('lambda')

def get_datetime_str():
    from datetime import datetime
    now = datetime.now()
    tt = now.timetuple()
    prefix = tt[0]
    name = '-'.join(['{:02}'.format(t) for t in tt[1:-3]])
    suffix = '{:03d}'.format(now.microsecond)[:3]
    job_name_suffix = "{}-{}-{}".format(prefix, name, suffix)
    return job_name_suffix

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))

    msg = {}
    cfg = {}
    cfg['input_train_bucket'] = os.environ['INPUT_TRAIN_BUCKET']
    cfg['input_test_bucket'] = os.environ['INPUT_TEST_BUCKET']
    cfg['output_bucket'] = os.environ['OUTPUT_BUCKET']
    cfg['hparams'] = os.environ['HPARAMS']
    cfg['date'] = get_datetime_str()
    cfg['name'] = os.environ['NAME']
    cfg['image_uri'] = os.environ['IMAGE_URI']
    cfg['sagemaker_role'] = os.environ['SAGEMAKER_ROLE']
    cfg['instance'] = os.environ['INSTANCE']

    try:
        job_arn = create_training_job(**cfg)["TrainingJobArn"]
        msg = {"Status": "Success", "TrainingJob": job_arn.split("/")[1]}
    except Exception as e:
        msg = {"Status": "Failure", "Message": str(e)}
    print(msg)

    response = {
        "statusCode": 200,
        "body": json.dumps(msg),
        "headers": {
            "Content-Type": "application/json",
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
    }
    print(response)

    return response
    # return json.loads(responce)