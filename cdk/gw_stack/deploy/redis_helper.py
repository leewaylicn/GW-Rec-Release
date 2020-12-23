from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_lambda as _lambda,
                     aws_s3 as s3)


class GWRedisHelper:

    def __init__(self):
        self.name='RedisHelper'

    @staticmethod
    def create_redis(stack, vpc, is_group=False):
        print(vpc.private_subnets)
        subnetGroup = ec.CfnSubnetGroup(
            stack,
            "RedisClusterPrivateSubnetGroup-test",
            cache_subnet_group_name="recommendations-redis-subnet-group-test",
            description="Redis subnet for recommendations",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets]
        )

        redis_security_group = ec2.SecurityGroup(
            stack, 
            "redis-security-group-test", 
            vpc=vpc
        )

        redis_connections = ec2.Connections(
            security_groups=[redis_security_group], 
            default_port=ec2.Port.tcp(6379)
        )
        redis_connections.allow_from_any_ipv4(port_range=ec2.Port.tcp(6379))


        if is_group:
            #group
            redis = ec.CfnReplicationGroup(
                stack,
                "RecommendationsRedisCacheCluster",
                engine="redis",
                cache_node_type="cache.t2.small",
                replicas_per_node_group=1,
                num_node_groups=3,
                replication_group_description="redis-gw-test",
                automatic_failover_enabled=True,
                security_group_ids=[redis_security_group.security_group_id],
                cache_subnet_group_name=subnetGroup.cache_subnet_group_name
            )
        else:
            # one node
            redis = ec.CfnCacheCluster(
                stack,
                "RecommendationsRedisCacheCluster",
                engine="redis",
                cache_node_type="cache.t2.small",
                num_cache_nodes=1,
                cluster_name="redis-gw-test",
                vpc_security_group_ids=[redis_security_group.security_group_id],
                cache_subnet_group_name=subnetGroup.cache_subnet_group_name
            )


        # no python sample, this is nodejs sample for group mode
        '''
        const redisReplication = new CfnReplicationGroup(
            this,
            `RedisReplicaGroup`,
            {
                engine: "redis",
                cacheNodeType: "cache.m5.xlarge",
                replicasPerNodeGroup: 1,
                numNodeGroups: 3,
                automaticFailoverEnabled: true,
                autoMinorVersionUpgrade: true,
                replicationGroupDescription: "cluster redis di produzione",
                cacheSubnetGroupName: redisSubnetGroup.cacheSubnetGroupName
            }
            );
        '''
        
        redis.add_depends_on(subnetGroup)

        if is_group:
            return redis.attr_primary_end_point_address,redis.attr_primary_end_point_port
        else:
            return redis.attr_redis_endpoint_address, redis.attr_redis_endpoint_port
