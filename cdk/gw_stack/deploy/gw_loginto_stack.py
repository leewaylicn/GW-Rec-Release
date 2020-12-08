from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_iam as iam)
from .ecs_helper import GWEcsHelper
from .gw_helper import GWAppHelper


class GWLogintoStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, 
            vpc: ec2.Vpc, ecs_role: iam.Role, redis_host:str, 
            redis_port:int,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        image = "233121040379.dkr.ecr.cn-northwest-1.amazonaws.com.cn/loginto_aws:20201205_01"
        name = "loginto_aws"
        env = {
            #"MODEL_S3_KEY":"s3://rp-gw/dkn/model/model.tar.gz"
            "IR_APP_CONFIG":"/opt/config/zhinengfenfaupdater/config.ini",
            "AWS_REDIS_CLUSTER":"0",
            "AWS_REDIS_PASSWORD":"",
            "AWS_REDIS_DB":"0",
            "AWS_KAFKA_HOST":"10.10.20.65:9092,10.10.20.78:9092,10.10.20.37:9092",
            "AWS_REDIS_HOST":redis_host,
            "AWS_REDIS_PORT":redis_port
        }

        self.url = GWEcsHelper.create_fagate_ALB_autoscaling(
            self,
            vpc,
            image,
            name,
            port=8001,
            ecs_role=GWAppHelper.create_ecs_role(self),
            env=env
        )