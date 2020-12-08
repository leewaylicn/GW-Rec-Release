from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_lambda as _lambda,
                     aws_s3 as s3, aws_lambda_event_sources as lambda_event_source, aws_iam as iam)


class GWIAMHelper:

    def __init__(self):
        self.name='IAMHelper'

    @staticmethod
    def create_ecs_role(stack):
        ecs_role = iam.Role(
            stack, 
            'FargateTaskExecutionServiceRole', 
            assumed_by = iam.ServicePrincipal('ecs-tasks.amazonaws.com')    
        )

        ecs_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect('ALLOW'),
                resources=['*'],
                actions=[            
                    'ecr:GetAuthorizationToken',
                    'ecr:BatchCheckLayerAvailability',
                    'ecr:GetDownloadUrlForLayer',
                    'ecr:BatchGetImage',
                    'logs:CreateLogStream',
                    'logs:PutLogEvents'
                ]
            )
        )

        return ecs_role
