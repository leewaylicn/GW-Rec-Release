config = {}

config["job_level"] = {
    "sagemaker_role": "AirflowInstanceRole",
    "region_name": "cn-north-1",  # replace
    "run_hyperparameter_opt": "no"
}

config["train_dkn"] = {
    "estimator_config": {
        "train_instance_count": 1,
        "train_instance_type": 'ml.p3.2xlarge',
        "output_path": "s3://rp-gw/dkn_model/",  # replace
        "base_job_name": "dkn",
        "hyperparameters": {
            'learning_rate': 0.0001,
            'servable_model_dir': '/opt/ml/model',
            'loss_weight': 1.0,
            'use_context': True,
            'max_click_history': 30,
            'num_epochs': 1,
            'max_title_length': 16,
            'entity_dim': 128,
            'word_dim': 300,
            'batch_size': 128,
            'perform_shuffle': 1,
            'checkpointPath': '/opt/ml/checkpoints'
        }
    },
    "inputs": {
        "train": "s3://rp-gw/train.csv/",  # replace
        "test": "s3://rp-gw/test.csv/",  # replace
    }
}

config['ecs_task_definition'] = {
    "requiresCompatibilities": [
        "FARGATE"
    ],
    "memory": "8192",
    "cpu": "4096",
    "containerDefinitions": [{
        "name": "EC2TFInference",
        "image": "856419311962.dkr.ecr.cn-north-1.amazonaws.com.cn/gw-infer:latest",
        "environment": [
            {
                "name": "MODEL_S3_KEY",
                "value": "s3://leigh-gw/dkn_model/dkn-2020-11-28-06-41-17-782/output/model.tar.gz"
            }
        ],
        "essential": True,
        "portMappings": [
            {
                "hostPort": 8500,
                "protocol": "tcp",
                "containerPort": 8500
            },
            {
                "hostPort": 8501,
                "protocol": "tcp",
                "containerPort": 8501
            },
            {
                "containerPort": 80,
                "protocol": "tcp"
            }
        ],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "gw-logs",
                "awslogs-region": "cn-north-1",
                "awslogs-stream-prefix": "inference"
            }
        }
    }],
    "volumes": [],
    "networkMode": "awsvpc",
    "placementConstraints": [],
    "family": "cdkstackinferdknDKNinferenceTaskD52D2EA2",  # replace
    "taskRoleArn": "arn:aws-cn:iam::856419311962:role/ecsTaskExecutionRole",
    "executionRoleArn": "arn:aws-cn:iam::856419311962:role/ecsTaskExecutionRole"
}

config['run_task'] = {
    'cluster': 'arn:aws-cn:ecs:cn-north-1:856419311962:cluster/cdk-stack-infer-dkn-DKNinferencefargateserviceautoscaling22E4AB44-Llh81Z2M2qGc',  # replace
    'taskDefinition': 'arn:aws:ecs:cn-north-1:662566784674:task-definition/GW-DKN-infer:1',
    'count': 1,
    'launchType': 'FARGATE',
    'networkConfiguration': {
        'awsvpcConfiguration': {
            'subnets': [
                'subnet-09429633deda504bb', 'subnet-0cb5bad527af3b4d8'  # replace
            ],
            'securityGroups': [
                'sg-0988e2954825fae1b',  # replace
            ],
            'assignPublicIp': 'ENABLED'
        }
    },
    'overrides': {
        'executionRoleArn': 'arn:aws-cn:iam::856419311962:role/ecsTaskExecutionRole',  # replace with S3 get permission
        'taskRoleArn': 'arn:aws-cn:iam::856419311962:role/ecsTaskExecutionRole',  # replace
    }
}

config['ecs_service_update'] = {
    'cluster': 'arn:aws-cn:ecs:cn-north-1:856419311962:cluster/cdk-stack-infer-dkn-DKNinferencefargateserviceautoscaling22E4AB44-Llh81Z2M2qGc',  # replace
    "service": "test",
    "forceNewDeployment": True,
    "taskDefinition": ""
}
