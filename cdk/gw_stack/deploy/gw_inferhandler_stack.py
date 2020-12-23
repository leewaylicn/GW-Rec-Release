from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_iam as iam)
from .ecs_helper import GWEcsHelper
from .gw_helper import GWAppHelper

class GWInferHandlerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, 
            vpc: ec2.Vpc, ecs_role: iam.Role, graph_url: str, dkn_url: str,redis_host:str,redis_port:int, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
                
        #image = "856419311962.dkr.ecr.cn-north-1.amazonaws.com.cn/recsys-graph-dkn-inference"
        image = "233121040379.dkr.ecr.cn-northwest-1.amazonaws.com.cn/recsys-handler-inference:latest"
        name = "InferHandler"
        port = 9008
        env = {
            "GRAPH_URL":graph_url,
            "DKN_URL":dkn_url,
             "REDIS_URL":redis_host,
            "REDIS_PORT":redis_port
        }
        print(env)

        GWEcsHelper.create_fagate_ALB_autoscaling(
            self,
            vpc,
            image,
            name,
            ecs_role = GWAppHelper.create_ecs_role(self),
            env=env,
            port=port,
            public_load_balancer=True,
            desired_count=10
        )


    ########################################################
    #    The full run version, before resturcture
    ########################################################

    # def __init__(self, scope: core.Construct, id: str, 
    #             **kwargs) -> None:
    #     super().__init__(scope, id, **kwargs)

    #     image = 'nginx'
    #     port = 80
    #     name = 'Nginx'
    #     env = ''

    #     vpc = ec2.Vpc(self, "GWVpc", max_azs=3)     # default is all AZs in region
        
    #     cluster = ecs.Cluster(
    #         self, 
    #         name+'fargate-service-autoscaling', 
    #         vpc=vpc
    #     )

    #     task = ecs.FargateTaskDefinition(
    #         self,
    #         name+'-Task',
    #         memory_limit_mib=512,
    #         cpu=256,
    #     )

    #     if port is not None:
    #         task.add_container(
    #             name+'-Contaner',
    #             image=ecs.ContainerImage.from_registry(image),
    #             #environment=env
    #         ).add_port_mappings(
    #                 ecs.PortMapping(container_port=port)
    #         )
    #     else:
    #         task.add_container(
    #             name+'-Contaner',
    #             image=ecs.ContainerImage.from_registry(image),
    #             #environment=env
    #         )

    #     # Create Fargate Service
    #     fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
    #         self,
    #         name+"-Service",
    #         cluster=cluster,
    #         task_definition=task
    #     )

    #     fargate_service.service.connections.security_groups[
    #         0].add_ingress_rule(peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
    #                             connection=ec2.Port.tcp(port),
    #                             description="Allow http inbound from VPC")

    #     # Setup AutoScaling policy
    #     scaling = fargate_service.service.auto_scale_task_count(max_capacity=2)
    #     scaling.scale_on_cpu_utilization(
    #         "CpuScaling",
    #         target_utilization_percent=50,
    #         scale_in_cooldown=core.Duration.seconds(60),
    #         scale_out_cooldown=core.Duration.seconds(60),
    #     )

    #     core.CfnOutput(
    #         self, 
    #         name+'ServiceURL',    
    #         value='http://{}/'.format(fargate_service.load_balancer.load_balancer_full_name)
    #     )
  