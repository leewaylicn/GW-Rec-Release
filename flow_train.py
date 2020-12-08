import copy
from datetime import datetime, timedelta
from airflow.models import Variable
from airflow.contrib.operators.ecs_operator import ECSOperator

import airflow
from airflow import DAG
from airflow.contrib.operators.sagemaker_training_operator import SageMakerTrainingOperator
from airflow.contrib.operators.sagemaker_transform_operator import SageMakerTransformOperator

import sagemaker
from sagemaker.tensorflow import TensorFlow
from sagemaker.workflow.airflow import training_config, transform_config_from_estimator
from airflow.operators.python_operator import PythonOperator

# step - train DKN

train_instance_type = 'ml.p3.2xlarge'

hyperparameters = {'learning_rate': 0.0001,
                   'servable_model_dir': '/opt/ml/model',
                   'loss_weight': 1.0,
                   'use_context': True,
                   'max_click_history': 30,
                   'num_epochs': 1,
                   'max_title_length': 16,
                   'entity_dim': 128,
                   'word_dim': 300,
                   'batch_size': 128,
                   'perform_shuffle': 1,
                   'checkpointPath': '/opt/ml/checkpoints'}

byoc_est = sagemaker.estimator.Estimator('662566784674.dkr.ecr.ap-northeast-1.amazonaws.com/gw-dkn:20201114025113',
                                         role=sagemaker.get_execution_role(),
                                         train_instance_count=1,
                                         train_instance_type=train_instance_type,
                                         base_job_name='dkn-byoc',
                                         hyperparameters=hyperparameters)

train_s3 = "s3://leigh-gw/train.csv/"
test_s3 = "s3://leigh-gw/test.csv/"
inputs = {'train': train_s3, 'eval': test_s3}

train_config = training_config(estimator=byoc_est,inputs=inputs)

# step - trigger CDK to deploy model as ECS service using Airflow Python Operator
def dkn_model_deploy(data, **context):
    print("mock for dkn deployment")

default_args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2),
    'provide_context': True
}

dag = DAG('tensorflow_example', default_args=default_args,
          schedule_interval='@once')

train_op = SageMakerTrainingOperator(
    task_id='tf_training',
    config=train_config,
    wait_for_completion=True,
    dag=dag)

deploy_op = PythonOperator(
    task_id='model_deploy',
    python_callable=dkn_model_deploy,
    op_args=['gw1','gw2'],
    provide_context=True,
    dag=dag)

deploy_op.set_upstream(train_op)
