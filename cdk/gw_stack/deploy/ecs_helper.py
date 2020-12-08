from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_lambda as _lambda,
                     aws_s3 as s3, aws_lambda_event_sources as lambda_event_source, aws_iam as iam)


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

    def create_fagate_ALB_autoscaling(stack, vpc, image, name, ecs_role=None, env=None, port=None):
        cluster = ecs.Cluster(
            stack, 
            name+'fargate-service-autoscaling', 
            vpc=vpc
        )

        ecs_log = ecs.LogDrivers.aws_logs(stream_prefix=name)

        if ecs_role is not None:
            task = ecs.FargateTaskDefinition(
                stack,
                name+'-Task',
                memory_limit_mib=512,
                cpu=256,
                execution_role=ecs_role, 
                task_role=ecs_role
            )
        else:
            task = ecs.FargateTaskDefinition(
                stack,
                name+'-Task',
                memory_limit_mib=512,
                cpu=256
            )

        if env is None:
            env = {"test": "test"}

        print(env)
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
                listener_port=port
            )
        else:
            fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
                stack,
                name+"-Service",
                cluster=cluster,
                task_definition=task,
                assign_public_ip=True
            )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(port),
            description="Allow http inbound from VPC"
        )

        # Setup AutoScaling policy
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=2)
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )
        '''
        core.CfnOutput(
            stack, 
            name+'ServiceURL',    
            value='http://{}/'.format(fargate_service.load_balancer.load_balancer_full_name),
            export_name=name+'URL'
        )
        '''
        
        return fargate_service.load_balancer.load_balancer_dns_name

    