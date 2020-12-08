import copy
from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.contrib.operators.ecs_operator import ECSOperator

# Airflow Variables
awsRegionName = Variable.get('AwsRegionName')
awsCluster = Variable.get('AwsCluster')
awsTaskDefinition = Variable.get('AwsTaskDefinition')
awsNetworkSubnet = Variable.get('AwsNetworkSubnet')
awsContainerName = Variable.get('AwsContainerName')
startYear = int(Variable.get('StartYear'))
endYear = int(Variable.get('EndYear'))

yearsToAnalyze = list(range(startYear, endYear))

AIRFLOW_ECS_OPERATOR_RETRIES = 2

# DAG base information
dag = DAG(
    dag_id = 'analyzer',
    default_args = {
        'owner': 'terrance',
        'start_date': datetime(2020, 1, 2)
    },
    schedule_interval = None,
)
# ECS Operator arguments template
ecs_operator_args_template = {
    'aws_conn_id' : 'aws_default',              
    'region_name' : awsRegionName,              
    'launch_type' : 'FARGATE',
    'cluster' : awsCluster,                     
    'task_definition' : awsTaskDefinition,      
    'network_configuration' : {
        'awsvpcConfiguration' : {
            'assignPublicIp' : 'ENABLED',
            'subnets' : [ awsNetworkSubnet ]       
        }
    },
    'awslogs_group' : '/ecs/' + awsTaskDefinition,
    'awslogs_stream_prefix' : 'ecs/' + awsContainerName,
    'overrides' : {
        'containerOverrides' : [
            {
                'name': awsContainerName,
                'memoryReservation': 500,
            },
        ],
    },
}

# Create ECS operators
task_list = []

for index in range(len(yearsToAnalyze)):
    ecs_operator_args = copy.deepcopy(ecs_operator_args_template)
    ecs_operator_args['overrides']['containerOverrides'][0]['command'] = ['-y', str(yearsToAnalyze[index])]
    ecs_operator = ECSOperator(
        task_id = str(yearsToAnalyze[index]),
        dag = dag,
        retries = AIRFLOW_ECS_OPERATOR_RETRIES,
        retry_delay = timedelta(seconds=10),
        **ecs_operator_args
    )
    task_list.append(ecs_operator)