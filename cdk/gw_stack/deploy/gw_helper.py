from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_lambda as _lambda,
                     aws_s3 as s3, aws_lambda_event_sources as lambda_event_source, aws_iam as iam)


class GWAppHelper:

    def __init__(self):
        self.name='GWAppHelper'

    def create_trigger_training_task(self, **kwargs):
        ####################
        # Unpack Value
        name = kwargs['name'].replace("_","-")
        lambda_name = "{}-lambda".format(name)
        code_name = "{}".format(name)
        job_name = "{}-job".format(name)
        task = "{}-task".format(name)
        instance = kwargs['instance']
        image_uri = kwargs['image_uri']
        trigger_bucket = kwargs['trigger_bucket']
        input_train_bucket = kwargs['input_train_bucket']
        input_validation_bucket = kwargs['input_validation_bucket']
        # hparams = kwargs['hparams']
        output_bucket = kwargs['output_bucket']
        lambda_train_role = kwargs['lambda_role']
        sagemaker_train_role = kwargs['sagemaker_role'].role_arn

        # Create Lambda
        lambda_app = _lambda.Function(self, lambda_name,
            handler='{}.handler'.format(code_name),
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda'),
            role=lambda_train_role,
            environment={
                'INPUT_TRAIN_BUCKET': input_train_bucket,
                'INPUT_VALIDATION_BUCKET': input_validation_bucket,
                'OUTPUT_BUCKET': output_bucket,
                'NAME': name,
                'IMAGE_URI': image_uri,
                'SAGEMAKER_ROLE': sagemaker_train_role,
                # 'HPARAMS': hparams,
                'INSTANCE': instance
            }
        )
        # Create an S3 event soruce for Lambda
        bucket = s3.Bucket(self, trigger_bucket)
        s3_event_source = lambda_event_source.S3EventSource(bucket, events=[s3.EventType.OBJECT_CREATED])
        lambda_app.add_event_source(s3_event_source)

        return lambda_app

    def get_datetime_str():
        from datetime import datetime
        now = datetime.now()
        tt = now.timetuple()
        prefix = tt[0]
        name = '-'.join(['{:02}'.format(t) for t in tt[1:-3]])
        suffix = '{:03d}'.format(now.microsecond)[:3]
        job_name_suffix = "{}-{}-{}".format(prefix, name, suffix)
        return job_name_suffix



    def create_lambda_train_role(self, name):
        # Config role
        base_role = iam.Role(
            self,
            "gw_lambda_train_role_{}".format(name),
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"))

        return base_role 
        
    def create_sagemaker_train_role(self, name):
        # Config role
        base_role = iam.Role(
            self,
            "gw_sagemaker_train_role_{}".format(name),
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com")
        )
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"))
        #base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonElasticContainerRegistryPublicFullAccess"))
        #base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryPublicFullAccess"))
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryFullAccess"))

        return base_role    
        
    def create_ecs_role(self):
        ecs_role = iam.Role(
            self, 
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

        ecs_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        ecs_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess"))
        ecs_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"))

        return ecs_role 
