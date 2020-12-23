from aws_cdk import (core, 
                     aws_ec2 as ec2, 
                     aws_ecs as ecs, 
                     aws_ecr as ecr,
                     aws_ecs_patterns as ecs_patterns, 
                     aws_elasticache as ec,
                     aws_rds as rds,
                     aws_apigateway as apigw,
                     aws_iam as iam,
                     aws_lambda as _lambda,    
                     aws_s3 as s3,
                     aws_lambda_event_sources as lambda_event_source
                    )

from .gw_helper import GWAppHelper
from .ecs_helper import GWEcsHelper

import json

class GWGraphTrainStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        graph_train_image = '233121040379.dkr.ecr.cn-northwest-1.amazonaws.com.cn/gw-graph-train:latest'

        cfg_dict = {}
        cfg_dict['vpc'] = vpc
        cfg_dict['name'] = 'graph-train'
        cfg_dict['date'] = GWAppHelper.get_datetime_str()
        cfg_dict['trigger_bucket']= "{}-bucket-event-{}".format(cfg_dict['name'], cfg_dict['date'])
        cfg_dict['input_train_bucket']= "{}-train_bucket".format(cfg_dict['name'])
        cfg_dict['input_validation_bucket']= "{}-validation-bucket".format(cfg_dict['name'])
        cfg_dict['output_bucket']= "{}-bucket-model-{}".format(cfg_dict['name'], cfg_dict['date'])
        cfg_dict['ecr'] = 'sagemaker-recsys-graph-train'
        cfg_dict['instance'] = "ml.g4dn.xlarge"
        cfg_dict['image_uri'] = graph_train_image 
        lambda_train_role = GWAppHelper.create_lambda_train_role(self, cfg_dict['name'])
        sagemaker_train_role = GWAppHelper.create_sagemaker_train_role(self, cfg_dict['name'])
        cfg_dict['lambda_role'] = lambda_train_role
        cfg_dict['sagemaker_role'] = sagemaker_train_role
    
        self.graph_train = GWAppHelper.create_trigger_training_task(self, **cfg_dict)