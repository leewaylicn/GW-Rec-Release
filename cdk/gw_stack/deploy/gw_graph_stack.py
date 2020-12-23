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

class GWGraphStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, redis_host:str,
            redis_port:int,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

       # vpc = ec2.Vpc(self, "GWVpc", max_azs=3)     # default is all AZs in region

        graph_infer_image = '233121040379.dkr.ecr.cn-northwest-1.amazonaws.com.cn/sagemaker-recsys-graph-inference:latest'
        name = "graph-inference"
        # port = 8080
        port = 8501
        env = {
            # "MODEL_S3_KEY":"s3://rp-gw/dkn/model/model.tar.gz",
            # "MODEL_S3_KEY":"s3://rp-gw-1/dkn_model/dkn-2020-12-03-11-53-53-391/output/model.tar.gz"
            "GRAPH_BUCKET": "recommend-gw-1",
            "KG_DBPEDIA_KEY": "dkn_model/kg_dbpedia.txt",
            "KG_ENTITY_KEY": "dkn_model/entities_dbpedia.dict",
            "KG_RELATION_KEY": "dkn_model/relations_dbpedia.dict",
            "KG_ENTITY_INDUSTRY_KEY": "dkn_model/entity_industry.txt",
            "KG_VOCAB_KEY": "dkn_model/vocab.json",
            "DATA_INPUT_KEY": "data/input",
            "TRAIN_OUTPUT_KEY": "train/output"
        }

        self.url = GWEcsHelper.create_fagate_ALB_autoscaling(
            self,
            vpc,
            graph_infer_image,
            name,
            ecs_role = GWAppHelper.create_ecs_role(self),
            env=env,
            port=port
        )
        #cfg_dict = {}
        #cfg_dict['function'] = 'graph_inference'
        #cfg_dict['ecr'] = 'sagemaker-recsys-graph-inference'
        #graph_inference_dns = self.create_fagate_NLB_autoscaling_custom(vpc, **cfg_dict)

        #cfg_dict['function'] = 'graph_train'
        #cfg_dict['ecr'] = 'sagemaker-recsys-graph-train'
        #cfg_dict['instance'] = "ml.g4dn.xlarge"
        #cfg_dict['image_uri'] = '002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-graph-train'
        #self.create_lambda_trigger_task_custom(vpc, **cfg_dict)

        # ####################
        # # test for dkn training
        # cfg_dict['name'] = 'dkn-train'
        # cfg_dict['trigger_bucket']= "{}-bucket-event".format(cfg_dict['name'])
        # #cfg_dict['input_bucket']= "{}-bucket-model-{}".format(cfg_dict['name'], cfg_dict['date'])
        # #cfg_dict['output_bucket']= "{}-bucket-model-{}".format(cfg_dict['name'], cfg_dict['date'])

        # hyperparameters = {'learning_rate': '0.0001',  'servable_model_die': '/opt/ml/model', 'loss_weight': '1.0', 
        # 'use_context': 'True', 'max_click_history': '30',  'num_epochs': '1', 'max_title_length': '16',  'entity_dim': '128', 
        # 'word_dim': '300',  'batch_size': '128',  'perform_shuffle': '1', 'checkpointPath': '/opt/ml/checkpoints'}

        # cfg_dict['hparams'] = json.dumps(hyperparameters)
        # cfg_dict['input_train_bucket'] = "autorec-great-wisdom/train.csv/"
        # cfg_dict['input_validation_bucket'] = "autorec-great-wisdom/test.csv/"
        # cfg_dict['output_bucket'] = "autorec-great-wisdom/output_model/"
        # cfg_dict['ecr'] = 'sagemaker-recsys-dkn-train'
        # cfg_dict['instance'] = "ml.p2.xlarge"
        # cfg_dict['image_uri'] = '002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-dkn-train'
        # cfg_dict['lambda_role'] = lambda_train_role
        # cfg_dict['sagemaker_role'] = sagemaker_train_role
        # self.dkn_train = GWAppHelper.create_trigger_training_task(self, **cfg_dict)
    
'''
    def create_redis(self, vpc):
        subnetGroup = ec.CfnSubnetGroup(
            self,
            "RedisClusterPrivateSubnetGroup",
            cache_subnet_group_name="recommendations-redis-subnet-group",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
            description="Redis subnet for recommendations"
        )

        redis_security_group = ec2.SecurityGroup(self, "redis-security-group", vpc=vpc)

        redis_connections = ec2.Connections(
            security_groups=[redis_security_group], default_port=ec2.Port.tcp(6379)
        )
        redis_connections.allow_from_any_ipv4(port_range=ec2.Port.tcp(6379))

        redis = ec.CfnCacheCluster(
            self,
            "RecommendationsRedisCacheCluster",
            engine="redis",
            cache_node_type="cache.t2.small",
            num_cache_nodes=1,
            cluster_name="redis-gw",
            vpc_security_group_ids=[redis_security_group.security_group_id],
            cache_subnet_group_name=subnetGroup.cache_subnet_group_name
        )
        redis.add_depends_on(subnetGroup)
# # 20201221 delete 
#     def create_fagate_ALB(self, vpc):
#         # Create ECS
#         cluster = ecs.Cluster(self, "GWCluster", vpc=vpc)

#         ecs_patterns.ApplicationLoadBalancedFargateService(
#             self, 
#             "GWService",
#             cluster=cluster,            # Required
#             cpu=256,                    # Default is 256
#             desired_count=20,            # Default is 1
#             task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
#                 image=ecs.ContainerImage.from_registry("856419311962.dkr.ecr.cn-north-1.amazonaws.com.cn/airflow_analyze"),
#                 container_port=80
#             ),
#             memory_limit_mib=512,      # Default is 512
#             public_load_balancer=True
#         )
    
    def create_fagate_NLB_autoscaling(self, vpc):
        cluster = ecs.Cluster(
            self, 'fargate-service-autoscaling',
            vpc=vpc
        )

        # config IAM role
        # add managed policy statement
        ecs_base_role = iam.Role(
            self,
            "ecs_service_role",
            assumed_by=iam.ServicePrincipal("ecs.amazonaws.com")
        )
        ecs_role = ecs_base_role.from_role_arn(self, 'gw-ecr-role-test', role_arn='arn:aws:iam::002224604296:role/ecsTaskExecutionRole')

        # Create Fargate Task Definition
        fargate_task = ecs.FargateTaskDefinition(
            self, "graph-inference-task-definition", execution_role=ecs_role, task_role=ecs_role, cpu=2048, memory_limit_mib=4096
        )

        #ecr_repo = ecr.IRepository(self, "002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-graph-inference")
        ecr_repo = ecr.Repository.from_repository_name(self, id = "graph-inference-docker", repository_name = "sagemaker-recsys-graph-inference")

        port_mapping = ecs.PortMapping(
            container_port=8080,
            host_port=8001,
            protocol=ecs.Protocol.TCP
        )

        ecs_log = ecs.LogDrivers.aws_logs(stream_prefix='gw-inference-test')

        farget_container = fargate_task.add_container("graph-inference",image=ecs.ContainerImage.from_ecr_repository(ecr_repo), logging=ecs_log
        )
        farget_container.add_port_mappings(port_mapping)


        fargate_service = ecs.FargateService(self, 'graph-inference-service',
            cluster=cluster, task_definition=fargate_task, assign_public_ip=True
        )

        fargate_service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4('0.0.0.0/0'),
            connection = ec2.Port.tcp(8080),
            description = "Allow http inbound from VPC"
        )

        return fargate_service.load_balancer.load_balancer_dns_name

    def create_fagate_NLB_autoscaling_custom(self, vpc, **kwargs):
        ####################
        # Unpack Value for name/ecr_repo
        app_name = kwargs['function'].replace("_","-")
        task_name = "{}-task-definition".format(app_name)
        log_name = app_name
        image_name = "{}-image".format(app_name)
        container_name = "{}-container".format(app_name)
        service_name = "{}-service".format(app_name)

        app_ecr = kwargs['ecr']
        ecs_role = kwargs['ecs_role']

        ####################
        # Create Cluster
        cluster = ecs.Cluster(
            self, 'fargate-service-autoscaling',
            vpc=vpc
        )

        ####################
        # Config IAM Role
        # add managed policy statement
        # ecs_base_role = iam.Role(
        #     self,
        #     "ecs_service_role",
        #     assumed_by=iam.ServicePrincipal("ecs.amazonaws.com")
        # )
        # ecs_role = ecs_base_role.from_role_arn(self, 'gw-ecr-role-test', role_arn='arn:aws:iam::002224604296:role/ecsTaskExecutionRole')

        ####################
        # Create Fargate Task Definition
        fargate_task = ecs.FargateTaskDefinition(
            self, task_name, 
            execution_role=ecs_role, task_role=ecs_role, 
            cpu=2048, memory_limit_mib=8192
        )
        # 0. config log
        ecs_log = ecs.LogDrivers.aws_logs(stream_prefix=log_name)
        # 1. prepare ecr repository
        ecr_repo = ecr.Repository.from_repository_name(self, id = image_name, repository_name = app_ecr)
        farget_container = fargate_task.add_container(
            container_name,
            image=ecs.ContainerImage.from_ecr_repository(ecr_repo), 
            logging=ecs_log,
            environment={'KG_PATH':"s3://autorec-1","REDIS_URL":self.redis_host,"REDIS_PORT":self.redis_port}
        )
        # 2. config port mapping
        port_mapping = ecs.PortMapping(
            container_port=9008,
            host_port=9008,
            protocol=ecs.Protocol.TCP
        )
        farget_container.add_port_mappings(port_mapping)

        ####################
        # Config NLB service
        # fargate_service = ecs.FargateService(self, 'graph-inference-service',
        #     cluster=cluster, task_definition=fargate_task, assign_public_ip=True
        # )
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, service_name,
            cluster=cluster,
            task_definition=fargate_task,
            assign_public_ip=True,
            desired_count=20,
            listener_port=9008
        )
        # 0. allow inbound in sg
        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            # peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            peer = ec2.Peer.ipv4('0.0.0.0/0'),
            connection = ec2.Port.tcp(9008),
            description = "Allow http inbound from VPC"
        )
        
        
        # 1. setup autoscaling policy
        # autoscaling 自动scale
#         scaling = fargate_service.service.auto_scale_task_count(
#             max_capacity=50
#         )
#         scaling.scale_on_cpu_utilization(
#             "CpuScaling",
#             target_utilization_percent=50,
#             scale_in_cooldown=core.Duration.seconds(60),
#             scale_out_cooldown=core.Duration.seconds(60),
#         )



        return fargate_service.load_balancer.load_balancer_dns_name

    def create_lambda_trigger_task_custom(self, vpc, **kwargs):
        ####################
        # Unpack Value
        app_name = kwargs['function'].replace("_","-")
        lambda_name = "{}-lambda".format(app_name)
        code_name = "{}".format(app_name)
        trigger_bucket_name = "{}-bucket-event".format(app_name)
        train_bucket_name = "{}-bucket-model".format(app_name)
        job_name = "{}-job".format(app_name)
        task = "{}-task".format(app_name)
        instance = kwargs['instance']
        image_uri = kwargs['image_uri']

        # Config role
        lambda_base_role = iam.Role(
            self,
            "gw_lambda_train_graph_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        #lambda_base_role.add_managed_policy(iam.ManagedPolicy.from_managed_policy_name("AWSLambdaBasicExectutionRole", "arn:aws:iam:aws:policy/service-role/AWSLambdaBasicExecutionRole"))
        #lambda_base_role.add_managed_policy(iam.ManagedPolicy.from_managed_policy_name("AWSLambdaVPCAcessExecutionRole", "arn:aws:iam:aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"))
        #lambda_base_role.add_managed_policy(iam.ManagedPolicy.from_managed_policy_name("AmazonSageMakerFullAccess", "arn:aws:iam:aws:policy/AmazonSageMakerFullAccess"))
        lambda_base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))
        lambda_base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"))

        # Create Lambda
        lambda_app = _lambda.Function(self, lambda_name,
            handler='{}.handler'.format(code_name),
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda'),
            role=lambda_base_role,
            environment={
                'BUCKET': train_bucket_name,
                'JOB_NAME': job_name,
                'INSTANCE': instance,
                'IMAGE_URI': image_uri,
                'TASK': task,
                "REDIS_URL":self.redis_host,
                "REDIS_PORT":self.redis_port
            }
        )
        # Create an S3 event soruce for Lambda
        bucket = s3.Bucket(self, trigger_bucket_name)
        s3_event_source = lambda_event_source.S3EventSource(bucket, events=[s3.EventType.OBJECT_CREATED])
        lambda_app.add_event_source(s3_event_source)

        return lambda_app

    def create_rds(self, vpc):
        # Create DB
        rds_cluster = rds.DatabaseCluster(
            self, 
            'Database', 
            engine=rds.DatabaseClusterEngine.AURORA,
            master_user=rds.Login(
                    username='admin'
            ),
            instance_props=rds.InstanceProps(
               instance_type=ec2.InstanceType.of(
                   ec2.InstanceClass.BURSTABLE2, 
                   ec2.InstanceSize.SMALL
                ),
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE
                ),
                vpc = vpc 
            )
        )
        return rds_cluster

# function:
# 1. graph training
# 2. graph inference

class GraphInterface(core.Construct):

    @property
    def handler(self):
        return self._handler
    
    def __init__(self, scope: core.Construct, id: str, **kwargs):

        super().__init__(scope, id, **kwargs)
        ####################
        # Unpack for train/inference dns
        graph_train_dns = kwargs['graph_train_dns']
        graph_inference_dns = kwargs['graph_inference_dns']

        #
        # self._user_info_table = ddb.Table(
        #     self, 'UserInfoTable',
        #     partition_key={'name': 'user_id', 'type': ddb.AttributeType.STRING}
        # )

        # self._item_tag_table = ddb.Table(
        #     self, 'ItemTagTable',
        #     partition_key={'name': 'item_type', 'type': ddb.AttributeType.STRING}
        # )

        self._handler = _lambda.Function(
            self, 'GraphInterfaceHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='graphinterface.handler',
            code=_lambda.Code.asset('lambda'),
            environment={
                'GRAPH_TRAIN_DNS': graph_train_dns,
                'GRAPH_INFERENCE_DNS':graph_inference_dns,
                "REDIS_URL":self.redis_host,
                "REDIS_PORT":self.redis_port
            }
        )

        # self._user_info_table.grant_read_write_data(self.handler)
        # self._item_tag_table.grant_read_write_data(self.handler)
'''    

