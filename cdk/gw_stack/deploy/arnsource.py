import boto3
import re
def get_cluster_name(stack_name):
    client = boto3.client('ecs')
    clusterArns = client.list_clusters()['clusterArns']
    for clusterArn in clusterArns:
        match = re.search(stack_name+'(.*?)', clusterArn)
        if match:
            return clusterArn.split("/")[-1]
def get_cluster_service(clusterName):
 
    client = boto3.client('ecs')
    ServiceName = client.list_services(
        cluster=clusterName
    )['serviceArns'][0].split('/')
    
    return ServiceName[2]

 
def get_elbNames(clusterName,serviceName):
    client = boto3.client('ecs')
 
    ans = client.describe_services(
        cluster=clusterName,
        services=[serviceName],
    )
    elbclient = boto3.client('elbv2')   
    
   
     
    elbarn = elbclient.describe_target_groups(
        TargetGroupArns=[
            ans['services'][0]['loadBalancers'][0]['targetGroupArn']
        ]
    )['TargetGroups'][0]['LoadBalancerArns'][0]
    LoadBalancerName = elbarn.split('/',1)[1]
    targetgroupname = ans['services'][0]['loadBalancers'][0]['targetGroupArn'].split(':')[-1]
    containerName  = ans['services'][0]['loadBalancers'][0]['containerName']
    

    return containerName,LoadBalancerName,targetgroupname
        
def get_redis_name(stack_name):
    return stack_name
def get_lambda_name(stack_name):
    return stack_name
        