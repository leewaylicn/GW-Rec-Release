from __future__ import print_function
import json
import requests
from datetime import datetime

# airflow operators
import airflow
from airflow.models import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

# airflow sagemaker operators
from airflow.contrib.operators.sagemaker_training_operator \
    import SageMakerTrainingOperator
from airflow.contrib.operators.sagemaker_tuning_operator \
    import SageMakerTuningOperator
from airflow.contrib.operators.sagemaker_transform_operator \
    import SageMakerTransformOperator
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.contrib.hooks.sagemaker_hook import SageMakerHook

# sagemaker sdk
import boto3
import sagemaker
from sagemaker.amazon.amazon_estimator import get_image_uri
from sagemaker.estimator import Estimator
from sagemaker.tuner import HyperparameterTuner

# airflow sagemaker configuration
from sagemaker.workflow.airflow import training_config
from sagemaker.workflow.airflow import tuning_config
from sagemaker.workflow.airflow import transform_config_from_estimator

# ml workflow specific
import config as cfg

from airflow.operators.python_operator import PythonOperator


# =============================================================================
# functions
# =============================================================================

def get_sagemaker_role_arn(role_name, region_name):
    iam = boto3.client('iam', region_name=region_name)
    response = iam.get_role(RoleName=role_name)
    return response["Role"]["Arn"]


# =============================================================================
# setting up training, tuning and transform configuration
# =============================================================================


# read config file
config = cfg.config

# set configuration for tasks
hook = AwsHook(aws_conn_id='airflow-sagemaker')
region = config["job_level"]["region_name"]
sess = hook.get_session(region_name=region)
role = get_sagemaker_role_arn(config["job_level"]["sagemaker_role"], sess.region_name)

# define KG estimator

# define DKN estimator
train_dkn_estimator = Estimator(
    # image_name='662566784674.dkr.ecr.ap-northeast-1.amazonaws.com/gw-dkn:20201114025113',
    image_name='690669119032.dkr.ecr.cn-north-1.amazonaws.com.cn/gw-infer:20201128031052',
    role=role,
    sagemaker_session=sagemaker.session.Session(sess),
    **config["train_dkn"]["estimator_config"]
)

train_dkn_config = training_config(estimator=train_dkn_estimator, inputs=config["train_dkn"]["inputs"])


# trigger CDK to deploy model as ECS service using Airflow Python Operator
def task_def(data, **context):
    print('in deploy ...')
    sm_train_return = context['ti'].xcom_pull(key='return_value')
    model_s3_key = sm_train_return['Training']['ModelArtifacts']['S3ModelArtifacts']
    print(model_s3_key)

    task_def = config["ecs_task_definition"]
    task_def['containerDefinitions'][0]['environment'][0]['value'] = model_s3_key

    client = boto3.client('ecs', region_name='cn-north-1')
    print(task_def)
    task_definition = client.register_task_definition(**task_def)
    task_definition_arn = task_definition['taskDefinition']['taskDefinitionArn']

    return task_definition_arn


def deploy_model_ecs(data, **context):
    print('run ecs task to deploy model ...')
    task_definition_arn = context['ti'].xcom_pull(key='return_value')
    print(task_definition_arn)

    client = boto3.client('ecs')
    run_task_json = config['run_task']
    run_task_json['taskDefinition'] = task_definition_arn
    print(run_task_json)
    run_task_ret = client.run_task(**run_task_json)
    print(run_task_ret)


# =============================================================================
# define airflow DAG and tasks
# =============================================================================

# define airflow DAG
default_args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2),
    'provide_context': True
}

dag = DAG(dag_id='gw', default_args=default_args,
          schedule_interval='@once')

train_op = SageMakerTrainingOperator(
    task_id='tf_training',
    config=train_dkn_config,
    wait_for_completion=True,
    dag=dag)

task_def_op = PythonOperator(
    task_id='task_definition',
    python_callable=task_def,
    op_args=['gw1'],
    provide_context=True,
    dag=dag)

deploy_ecs_op = PythonOperator(
    task_id='run_task',
    python_callable=deploy_model_ecs,
    op_args=['gw1'],
    provide_context=True,
    dag=dag)

deploy_ecs_op.set_upstream(task_def_op)
task_def_op.set_upstream(train_op)
