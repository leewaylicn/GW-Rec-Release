import boto3
from iam_helper import IamHelper

#def create_training_job(bucket, jobname, task, image_uri, instance):
def create_training_job(**kwargs):
    input_bucket = kwargs['input_bucket']
    output_bucket = kwargs['output_bucket']
    date = kwargs['date']
    name = kwargs['name']
    # s3_path = "s3://{}/{}/".format(bucket, jobname)
    helper = IamHelper
    client = boto3.client("sagemaker")
    job_name = "ml-{}-{}".format(name,date) 
    account = IamHelper.get_account_id()
    region = IamHelper.get_region()
    partition = IamHelper.get_partition()
    # role_name = "AmazonSageMaker-ExecutionRole-20200512T121482"
    # role_arn = "arn:{}:iam::{}:role/service-role/{}".format(partition, account, role_name)
    s3_output_path = 's3://sagemaker-{}-{}/'.format(region, account)
    image_uri = kwargs['image_uri']
    role_arn = kwargs['sagemaker_role']
    instance = kwargs['instance']
    # s3_model_url = s3_output_path +'sagemaker-recsys-graph-train-2020-11-25-07-47-06-659/'
    s3_model_url = "s3://{}/".format(kwargs['output_bucket'])

    response = client.create_training_job(
        TrainingJobName = job_name,
        HyperParameters = {},
        AlgorithmSpecification={
            'TrainingImage': image_uri,
            'TrainingInputMode': 'File',
        },
        RoleArn = role_arn,
        InputDataConfig=[
            {
                'ChannelName': "training", # environment variable SM_CHANNEL_TRAINING and /opt/ml/input/data/training
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': s3_model_url,
                    },
                },
            },
        ],
        OutputDataConfig={
            'S3OutputPath':s3_model_url 
        },
        ResourceConfig = {
            'InstanceType': instance,
            'InstanceCount': 1,
            'VolumeSizeInGB': 64,
        },
        StoppingCondition = {
            'MaxRuntimeInSeconds': 600,
        },
    )
    return response

def create_endpoint(job_name, model_uri):
    print("Creating SageMaker Endpoint {} from {}".format(job_name, model_uri))
    helper = IamHelper
    client = boto3.client("sagemaker")
    account = IamHelper.get_account_id()
    region = IamHelper.get_region()
    partition = IamHelper.get_partition()
    role_name = "AmazonSageMaker-ExecutionRole-20200512T121482"
    role_arn = "arn:{}:iam::{}:role/service-role/{}".format(partition, account, role_name)
    s3_output_path = 's3://sagemaker-{}-{}/'.format(region, account)
    response = client.create_model(
        ModelName = job_name,
        PrimaryContainer = {
            "Image": "250779322837.dkr.ecr.cn-north-1.amazonaws.com.cn/autogluon-sagemaker-inference-dev",
            "ModelDataUrl": model_uri
        },
        ExecutionRoleArn = role_arn
    )
    response = client.create_endpoint_config(
        EndpointConfigName = job_name,
        ProductionVariants=[
            {
                'VariantName': 'AllTraffic',
                'ModelName': job_name,
                'InitialInstanceCount': 1,
                'InstanceType': 'ml.c5.large',
            },
        ]
    )
    response = client.create_endpoint(
        EndpointName = job_name,
        EndpointConfigName = job_name
    )

def describe_training_job(job):
    helper = IamHelper
    client = boto3.client("sagemaker")

    training_jobs = client.list_training_jobs(MaxResults=100).get("TrainingJobSummaries", [])
    names = [j['TrainingJobName'] for j in training_jobs]
    stats = []
    # print("names={}".format(str(names)))
    
    if job in names:
        response = client.describe_training_job(TrainingJobName=job)
        transitions = response["SecondaryStatusTransitions"]
        # status = transitions[-1].get("Status", "Unknown")
        stats = [t.get("Status", "") for t in transitions]

    return stats

def describe_training_job_artifact(job):
    helper = IamHelper
    client = boto3.client("sagemaker")

    training_jobs = client.list_training_jobs(MaxResults=100).get("TrainingJobSummaries", [])
    names = [j['TrainingJobName'] for j in training_jobs]
    artifacts = ""
    # print("names={}".format(str(names)))
    
    if job in names:
        response = client.describe_training_job(TrainingJobName=job)
        artifacts = response["ModelArtifacts"]["S3ModelArtifacts"]

    return artifacts

def describe_endpoint(job):
    client = boto3.client("sagemaker")
    endpoints = client.list_endpoints()
    names = [endpoint["EndpointName"] for endpoint in endpoints["Endpoints"]]
    stats = [endpoint["EndpointStatus"] for endpoint in endpoints["Endpoints"]]
    status = "NotStarted"
    if job in names:
        for idx, name in enumerate(names):
            if job == name:
                status = stats[idx]
    return status

def list_endpoints(job):
    client = boto3.client("sagemaker")
    endpoints = client.list_endpoints()
    names = [endpoint["EndpointName"] for endpoint in endpoints["Endpoints"]]
    stats = [endpoint["EndpointStatus"] for endpoint in endpoints["Endpoints"]]
    return [{"Name": n, "Status": s} for n, s in zip(names, stats)]
