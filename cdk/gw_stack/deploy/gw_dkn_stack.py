from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_iam as iam)
from .ecs_helper import GWEcsHelper
from .gw_helper import GWAppHelper
import json


class GWDknStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, 
            vpc: ec2.Vpc, ecs_role: iam.Role,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        dkn_infer_image = "856419311962.dkr.ecr.cn-north-1.amazonaws.com.cn/gw-dkn-infer:latest"
        dkn_train_image = "856419311962.dkr.ecr.cn-north-1.amazonaws.com.cn/gw-dkn-train:latest"
        # dkn_train_input = 
        # dkn_test_input = 
        # dkn_model_output = 
        # image = "233121040379.dkr.ecr.cn-northwest-1.amazonaws.com.cn/gw-infer:latest"
        name = "DKN-inference"
        port = 8501
        env = {
            "MODEL_S3_KEY":"s3://rp-gw/dkn/model_complete/model.tar.gz"
            # "MODEL_S3_KEY":"s3://rp-gw-1/dkn_model/dkn-2020-12-03-11-53-53-391/output/model.tar.gz"
        }

        self.url = GWEcsHelper.create_fagate_ALB_autoscaling(
            self,
            vpc,
            dkn_infer_image,
            name,
            ecs_role = GWAppHelper.create_ecs_role(self),
            env=env,
            port=port
        )

        ####################
        # test for dkn training
        cfg_dict = {}
        cfg_dict['name'] = 'dkn-train'
        cfg_dict['trigger_bucket']= "{}-bucket-event".format(cfg_dict['name'])
        lambda_train_role = GWAppHelper.create_lambda_train_role(self, cfg_dict['name'])
        sagemaker_train_role = GWAppHelper.create_sagemaker_train_role(self, cfg_dict['name'])

        #cfg_dict['input_bucket']= "{}-bucket-model-{}".format(cfg_dict['name'], cfg_dict['date'])
        #cfg_dict['output_bucket']= "{}-bucket-model-{}".format(cfg_dict['name'], cfg_dict['date'])

        hyperparameters = {'learning_rate': '0.0001',  'servable_model_dir': '/opt/ml/model', 'loss_weight': '1.0', 
        'use_context': 'True', 'max_click_history': '30',  'num_epochs': '1', 'max_title_length': '16',  'entity_dim': '128', 
        'word_dim': '300',  'batch_size': '128',  'perform_shuffle': '1', 'checkpointPath': '/opt/ml/input'}

        cfg_dict['hparams'] = json.dumps(hyperparameters)
        cfg_dict['input_train_bucket'] = "autorec-great-wisdom/train.csv/"
        cfg_dict['input_test_bucket'] = "autorec-great-wisdom/test.csv/"
        cfg_dict['output_bucket'] = "autorec-great-wisdom/output_model/"
        cfg_dict['ecr'] = 'sagemaker-recsys-dkn-train'
        cfg_dict['instance'] = "ml.p3.2xlarge"
        # image = "856419311962.dkr.ecr.cn-north-1.amazonaws.com.cn/gw-infer:latest"
        # cfg_dict['image_uri'] = '002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-dkn-train'
        cfg_dict['image_uri'] = dkn_train_image
        cfg_dict['lambda_role'] = lambda_train_role
        cfg_dict['sagemaker_role'] = sagemaker_train_role
        self.dkn_train = GWAppHelper.create_trigger_training_task(self, **cfg_dict)

