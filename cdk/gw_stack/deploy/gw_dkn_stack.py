from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_iam as iam)
from .ecs_helper import GWEcsHelper
from .gw_helper import GWAppHelper


class GWDknStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, 
            vpc: ec2.Vpc, ecs_role: iam.Role,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        dkn_infer_image = "233121040379.dkr.ecr.cn-northwest-1.amazonaws.com.cn/gw-dkn-infer:latest"
        # dkn_train_input = 
        # dkn_test_input = 
        # dkn_model_output = 
        # image = "233121040379.dkr.ecr.cn-northwest-1.amazonaws.com.cn/gw-infer:latest"
        name = "DKN-inference"
        port = 8501
        env = {
            #"MODEL_S3_KEY":"s3://rp-gw/dkn/model/model.tar.gz"
            "MODEL_S3_KEY":"s3://rp-gw-1/dkn_model/dkn-2020-12-03-11-53-53-391/output/model.tar.gz"
        }

        self.url = GWEcsHelper.create_fagate_ALB_autoscaling(
            self,
            vpc,
            dkn_infer_image,
            name,
            ecs_role = GWAppHelper.create_ecs_role(self),
            env=env,
            port=port,
            desired_count=60,
            public_load_balancer=True
        )

