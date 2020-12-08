from aws_cdk import (core, 
                     aws_ec2 as ec2, 
                     aws_ecs as ecs, 
                     aws_ecs_patterns as ecs_patterns, 
                     aws_elasticache as ec,
                     aws_rds as rds
                    )


class GWStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "GWVpc", max_azs=3)     # default is all AZs in region

        # # Create Redis
        # self.create_redis(vpc)

        #Create NLB autoscaling
        self.create_fagate_NLB_autoscaling(vpc)


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
    
    def create_fagate_ALB(self, vpc):
        # Create ECS
        cluster = ecs.Cluster(self, "GWCluster", vpc=vpc)

        ecs_patterns.ApplicationLoadBalancedFargateService(
            self, 
            "GWService",
            cluster=cluster,            # Required
            cpu=256,                    # Default is 256
            desired_count=1,            # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("856419311962.dkr.ecr.cn-north-1.amazonaws.com.cn/airflow_analyze"),
                container_port=80
            ),
            memory_limit_mib=512,      # Default is 512
            public_load_balancer=True
        )
    
    def create_fagate_NLB_autoscaling(self, vpc):
        cluster = ecs.Cluster(
            self, 'fargate-service-autoscaling',
            vpc=vpc
        )

        # Create Fargate Service
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "sample-app",
            cluster=cluster,
            task_image_options={
                'image': ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
            }
        )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )

        # Setup AutoScaling policy
        scaling = fargate_service.service.auto_scale_task_count(
            max_capacity=2
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )

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
    

