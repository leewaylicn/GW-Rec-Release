from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_lambda as _lambda,
                     aws_s3 as s3)


class GWRedisHelper:

    def __init__(self):
        self.name='RedisHelper'

    @staticmethod
    def create_redis(stack, vpc):
        print(vpc.private_subnets)
        subnetGroup = ec.CfnSubnetGroup(
            stack,
            "RedisClusterPrivateSubnetGroup",
            cache_subnet_group_name="recommendations-redis-subnet-group",
            description="Redis subnet for recommendations",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets]
        )

        redis_security_group = ec2.SecurityGroup(
            stack, 
            "redis-security-group", 
            vpc=vpc
        )

        redis_connections = ec2.Connections(
            security_groups=[redis_security_group], 
            default_port=ec2.Port.tcp(6379)
        )
        redis_connections.allow_from_any_ipv4(port_range=ec2.Port.tcp(6379))

        redis = ec.CfnCacheCluster(
            stack,
            "RecommendationsRedisCacheCluster",
            engine="redis",
            cache_node_type="cache.t2.small",
            num_cache_nodes=1,
            cluster_name="redis-gw",
            vpc_security_group_ids=[redis_security_group.security_group_id],
            cache_subnet_group_name=subnetGroup.cache_subnet_group_name
        )
        
        redis.add_depends_on(subnetGroup)

        return redis.attr_redis_endpoint_address, redis.attr_redis_endpoint_port
