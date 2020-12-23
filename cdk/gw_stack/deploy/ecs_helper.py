from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_lambda as _lambda,
                     aws_s3 as s3, aws_lambda_event_sources as lambda_event_source, aws_iam as iam,
                     aws_autoscaling as autoscaling)

from cdk_fargate_run_task import RunTask

class GWEcsHelper:

    def __init__(self):
        self.name='EcsHelper'

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

    @staticmethod
    def _create_fagate_queue_autoscaling(stack, vpc, image, name, 
            ecs_role=None, env=None, cpu=1024, memory=8192, 
            public_load_balancer=False, desired_count=1):

        cluster = ecs.Cluster(
            stack, 
            name+'fargate-service-autoscaling', 
            vpc=vpc
        )
# 20201220 delte
#         cluster.add_capacity(
#             name,
#             instance_type=ec2.InstanceType("c5.large")        
#         )

        ecs_log = ecs.LogDrivers.aws_logs(stream_prefix=name)

        if ecs_role is not None:
            task = ecs.FargateTaskDefinition(
                stack,
                name+'-Task',
                memory_limit_mib=memory,
                cpu=cpu,
                execution_role=ecs_role, 
                task_role=ecs_role
            )
        else:
            task = ecs.FargateTaskDefinition(
                stack,
                name+'-Task',
                memory_limit_mib=memory,
                cpu=cpu
            )

        if env is None:
            env = {"test": "test"}


        task.add_container(
                name+'-Contaner',
                image=ecs.ContainerImage.from_registry(image),
                logging=ecs_log,
                environment=env
        )

        ecs.FargateService(stack, name,
            cluster=cluster,
            task_definition=task,
            desired_count=desired_count
        )

        # deploy and run this task once
        #run_task_at_once = RunTask(stack, name, task=task)

        '''
        asg = autoscaling.AutoScalingGroup(
            self, "MyFleet",
            instance_type=ec2.InstanceType("t2.xlarge"),
            machine_image=ecs.EcsOptimizedAmi(),
            associate_public_ip_address=True,
            update_type=autoscaling.UpdateType.REPLACING_UPDATE,
            desired_capacity=1,
            vpc=vpc,
            vpc_subnets={ 'subnet_type': ec2.SubnetType.PUBLIC },
        )

        run_task_at_once.cluster.add_auto_scaling_group(asg)
        run_task_at_once.cluster.add_capacity(
            "DefaultAutoScalingGroup",
            instance_type=ec2.InstanceType("t2.xlarge")        
        )
        '''

        return "http://localhost"

    @staticmethod
    def _create_fagate_ALB_autoscaling(stack, vpc, image, name, 
            ecs_role=None, env=None, port=None, cpu=1024, memory=8192,
            public_load_balancer=False, desired_count=1):
        cluster = ecs.Cluster(
            stack, 
            name+'fargate-service-autoscaling', 
            vpc=vpc
        )

# #         2020-12-17-15注释
#         cluster.add_capacity(
#             name,
#             instance_type=ec2.InstanceType("c5.large")        
#         )

        ecs_log = ecs.LogDrivers.aws_logs(stream_prefix=name)

        if ecs_role is not None:
            task = ecs.FargateTaskDefinition(
                stack,
                name+'-Task',
                memory_limit_mib=memory,
                cpu=cpu,
                execution_role=ecs_role, 
                task_role=ecs_role
            )
        else:
            task = ecs.FargateTaskDefinition(
                stack,
                name+'-Task',
                memory_limit_mib=memory,
                cpu=cpu
            )

        if env is None:
            env = {"test": "test"}

        print(env)
        print({"test":"it is a port service"})
        if port is not None:
            task.add_container(
                name+'-Contaner',
                image=ecs.ContainerImage.from_registry(image),
                logging=ecs_log,
                environment=env
            ).add_port_mappings(
                    ecs.PortMapping(
                        container_port=port,
                        host_port=port,
                        protocol=ecs.Protocol.TCP
                    )
            )
        else:
            task.add_container(
                name+'-Contaner',
                image=ecs.ContainerImage.from_registry(image),
                logging=ecs_log,
                environment=env
            )

        # Create Fargate Service
        if port is not None:
            fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
                stack,
                name+"-Service",
                cluster=cluster,
                task_definition=task,
                assign_public_ip=True,
                public_load_balancer=public_load_balancer,
                listener_port=port,
                desired_count=desired_count
            )
        else:
            fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
                stack,
                name+"-Service",
                cluster=cluster,
                task_definition=task,
                public_load_balancer=public_load_balancer,
                assign_public_ip=True,
                desired_count=desired_count
            )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(port),
            description="Allow http inbound from VPC"
        )

        # Setup AutoScaling policy
#         scaling = fargate_service.service.auto_scale_task_count(max_capacity=2)
#         scaling.scale_on_cpu_utilization(
#             "CpuScaling",
#             target_utilization_percent=50,
#             scale_in_cooldown=core.Duration.seconds(60),
#             scale_out_cooldown=core.Duration.seconds(60),
#         )
        '''
        core.CfnOutput(
            stack, 
            name+'ServiceURL',    
            value='http://{}/'.format(fargate_service.load_balancer.load_balancer_full_name),
            export_name=name+'URL'
        )
        '''
        
        return fargate_service.load_balancer.load_balancer_dns_name

    @staticmethod
    def create_fagate_ALB_autoscaling(stack, vpc, image, name, 
            ecs_role=None, env=None, port=None, 
            public_load_balancer=False, desired_count=1):
    
        if port is not None:
            url=GWEcsHelper._create_fagate_ALB_autoscaling(stack, vpc, image, name, 
                ecs_role=ecs_role, 
                env=env, 
                port=port,
                public_load_balancer=public_load_balancer,
                desired_count=desired_count
            )
        else:
            url=GWEcsHelper._create_fagate_queue_autoscaling(stack, vpc, image, name, 
                ecs_role=ecs_role, 
                env=env,
                desired_count=desired_count
            )
        
        return url
