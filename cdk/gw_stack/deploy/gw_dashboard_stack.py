from aws_cdk import (
    aws_lambda as _lambda,
    aws_cloudwatch as cw,
    aws_s3 as s3,
    aws_cloudwatch as cw,
    aws_ecs,
    core
)
from .arnsource import (
    get_cluster_name,
    get_cluster_service,
    get_redis_name,
    get_lambda_name,
    get_elbNames
#     get_ec2_name
)
from aws_cdk.aws_cloudwatch import Metric, GraphWidget ,TextWidget
from aws_cdk.aws_elasticloadbalancingv2 import NetworkLoadBalancer,NetworkListener,Protocol
class GWDashboardStack(core.Stack):
    
    def __init__(self, scope: core.Construct, id: str, 
                 StackNames: dict ,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)
    
        
        #         {"metric_name":"",
#          "content":mycontent={
#                         namespace:String,
#                         identier:[{}{}{}],
#                         statistic='avg'
#                        }
#          }
#
        def buildwidget(titleName='Default',metrics=[]):
            lefts=[]
            for metric in metrics:
                statistic = metric['content']['statistic']
                namespace =  metric['content']['namespace']
                identiers= metric['content']['identier']
                tmp_lefts=[Metric(
                        namespace=namespace,
                        metric_name=metric['metricname'],
                        dimensions=item,
                        statistic=statistic
                        ) for item in identiers]
                for tmp_left in tmp_lefts:
                    lefts.append(tmp_left)
            return GraphWidget(
                title=titleName,
                left=lefts )
        dashboard = cw.Dashboard(self, "dashboard_gw",dashboard_name="eccom-gw-finall")
        
        def buildColumnELB(stackElbname,dashboard):
             
            clusterName = get_cluster_name(stackElbname)
            if clusterName==None:
                return dashboard
            ServiceName = get_cluster_service(clusterName)
            
            if ServiceName==None:
                return dashboard
            
            containerName,LoadBalancerName , LoadBalancerTargetgroup=get_elbNames(clusterName,ServiceName)
            ClusterMetric = [
                        { "ClusterName": clusterName,
                        "ServiceName": ServiceName
                        } 
            ]
            ELbidentierMul=[
                {"TargetGroup": LoadBalancerTargetgroup, "LoadBalancer":LoadBalancerName }
            ]
            ELbidentier=[
             { "LoadBalancer":LoadBalancerName }
            ]
            ClusterMetric=[
                        {'metricname': 'CPUUtilization',
                         'content': {'namespace': 'AWS/ECS', 
                                 'statistic': 'avg', 
                                 'identier':  ClusterMetric      
                                 }
                         } ,
                         {'metricname': 'MemoryUtilization',
                         'content': {'namespace': 'AWS/ECS', 
                                 'statistic': 'avg', 
                                 'identier': ClusterMetric 
                                 }
                         } 
            ]
            HostCountMetric=[
                        {'metricname': 'UnHealthyHostCount',
                         'content': {'namespace': 'AWS/NetworkELB', 
                                 'statistic': 'avg', 
                                 'identier': ELbidentierMul 
                                 }
                         },
                        {'metricname': 'HealthyHostCount',
                         'content': {'namespace': 'AWS/NetworkELB', 
                                 'statistic': 'avg', 
                                 'identier':  ELbidentierMul 
                                 }
                         } 
                
            ]
            ActiveFlowMetric=[
                        {'metricname': 'ActiveFlowCount',
                         'content': {'namespace': 'AWS/NetworkELB', 
                                 'statistic': 'avg', 
                                 'identier':ELbidentier
                                 }
                         }
                         
                
            ]
            ProcessedMetric=[
                        {'metricname': 'ProcessedBytes',
                         'content': {'namespace': 'AWS/NetworkELB', 
                                 'statistic': 'avg', 
                                 'identier':ELbidentier 
                                 }
                         }
                         
                
            ]
            dashboard.add_widgets(
                buildwidget(titleName=containerName+'ClusterMetric',metrics=ClusterMetric),
                buildwidget(titleName=containerName+'HostCountMetric',metrics=HostCountMetric),
                buildwidget(titleName=containerName+'ActiveFlowMetric',metrics=ActiveFlowMetric),
                buildwidget(titleName=containerName+'ProcessedMetric',metrics=ProcessedMetric),
                )
            return dashboard
        def buildColumnRedis(RedisName,dashboard):

            RedisCPUUtilization=[
                {'metricname': 'EngineCPUUtilization',
                 'content': {'namespace': 'AWS/ElastiCache', 
                         'statistic': 'avg', 
                         'identier': [
                                        { "CacheClusterId":RedisName} 
                                 ]
                         
                         }
                 } 
             ]
            RedisMemory=[
                        {'metricname': 'DatabaseMemoryUsagePercentage',
                         'content': {'namespace': 'AWS/ElastiCache', 
                                 'statistic': 'avg', 
                                 'identier': [
                                                { "CacheClusterId":RedisName}
                                         ]

                                 }
                         }
                
                    ]
            RedisCurrConnections=[
                        {'metricname': 'CurrConnections',
                         'content': {'namespace': 'AWS/ElastiCache', 
                                 'statistic': 'avg', 
                                 'identier': [
                                                { "CacheClusterId":RedisName}
                                         ]

                                 }
                         }
                
                    ]
            RedisCacheHitRate=[
                        {'metricname': 'CacheHitRate',
                         'content': {'namespace': 'AWS/ElastiCache', 
                                 'statistic': 'avg', 
                                 'identier': [
                                                { "CacheClusterId":RedisName}
                                         ]

                                 }
                         }
                
                    ]
            dashboard.add_widgets(
                buildwidget(titleName=RedisName+'EngineCPUUtilization',metrics=RedisCPUUtilization),
                buildwidget(titleName=RedisName+'DatabaseMemoryUsagePercentage',metrics=RedisMemory),
                buildwidget(titleName=RedisName+'CurrConnections',metrics=RedisCurrConnections),
                buildwidget(titleName=RedisName+'CacheHitRate',metrics=RedisCacheHitRate),
            )
            return dashboard

        def buildColumnec2(instanceids,dashboard):

            ec2identiers=[ {"InstanceId": instanceid} for instanceid in StackNames['ec2Stack']]
            EC2CPUUmetrics=[
                        {'metricname': 'CPUUtilization',
                         'content': {'namespace': 'AWS/EC2',
                                 'statistic': 'avg', 
                                 'identier': ec2identiers
                                 }
                        },
                    ]
            EC2Disk=[
                        {'metricname': 'DiskReadOps',
                         'content': {'namespace': 'AWS/EC2',
                                 'statistic': 'avg', 
                                 'identier':ec2identiers
                                 }
                        },
                        {'metricname': 'DiskWriteOps',
                         'content': {'namespace': 'AWS/EC2',
                                 'statistic': 'avg', 
                                 'identier':ec2identiers
                                 }
                        }
                    ]
            EC2NetworkIn=[
                        {'metricname': 'NetworkIn',
                         'content': {'namespace': 'AWS/EC2',
                                 'statistic': 'avg', 
                                 'identier':ec2identiers
                                 }
                        },
                    ]

            dashboard.add_widgets(
                buildwidget(titleName="EC2CPUUmetrics",metrics=EC2CPUUmetrics),
                buildwidget(titleName="EC2Disk",metrics=EC2Disk),
                buildwidget(titleName="EC2NetworkIn",metrics=EC2NetworkIn),
            )
            return dashboard



        def buildColumnlambda(FunctionName,dashboard):
            
            lambdaidentier=[
                                        { "FunctionName":FunctionName, 
                                         "Resource":FunctionName
                                        }
                                 ]
            InvocationsMetric=[
                {'metricname': 'Invocations',
                 'content': {'namespace': 'AWS/Lambda', 
                         'statistic': 'avg', 
                         'identier': lambdaidentier

                         }
                 }
            ]
            DurationMetric=[
                {'metricname': 'Duration',
                 'content': {'namespace': 'AWS/Lambda', 
                         'statistic': 'avg', 
                         'identier':lambdaidentier

                         }
                 }
            ]
            errorMetric=[
                {'metricname': 'NetworkRxErrors',
                 'content': {'namespace': 'AWS/Lambda', 
                         'statistic': 'avg', 
                         'identier': lambdaidentier
                         }
                 }
            ]
            dashboard.add_widgets(
                buildwidget(titleName="LambdaInvocation",metrics=InvocationsMetric),
                buildwidget(titleName="LambdaDuration",metrics=DurationMetric),
                buildwidget(titleName="Lamdaerror",metrics=errorMetric)
            )
            return dashboard


# ###########################elb##############################################
        dashboard.add_widgets(TextWidget(width=24,markdown="# ELB display\n这里是进行elb相关容器的指标展示"))
        print({"dashboard.node.unique_id":dashboard.node.unique_id})
        stackElbnames = StackNames['elbStack']
        if len(stackElbnames)!=0:
            print("11111111111111")
            for stackElbname in stackElbnames:
                dashboard = buildColumnELB(stackElbname,dashboard)
        
# # ###########################redis##############################################
        dashboard.add_widgets(TextWidget(width=24,markdown="# redis display\n这里是进行redis的指标展示"))
        stackRedisnames=StackNames['redisStack']
        if len(stackRedisnames)!=0:
 
            for stackRedisname in stackRedisnames:
                RedisName = get_redis_name(stackRedisname)
                dashboard = buildColumnRedis(RedisName,dashboard)
 #############################ec2####################################################
        dashboard.add_widgets(TextWidget(width=24,markdown="# ec2 display\n这里是进行ec2的指标展示"))
        ec2_instance_ids = StackNames['ec2Stack']
        
        if len(ec2_instance_ids)!=0:
            print({"ec2_instance_ids":len(ec2_instance_ids)})
            dashboard = buildColumnec2(ec2_instance_ids,dashboard)
################################Lambda#################################
        dashboard.add_widgets(TextWidget(width=24,markdown="# lambda display\n这里是进行lambda的指标展示"))
        stacklambdaStacknames=StackNames['lambdaStack']
        if len(stacklambdaStacknames)!=0:
            for stackRedisname in stacklambdaStacknames:
                RedisName = get_redis_name(stackRedisname)
                dashboard = buildColumnRedis(FunctionName,dashboard)