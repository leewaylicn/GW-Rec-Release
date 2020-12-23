#!/bin/bash

name=$1
image=$2
cpu=$3
memory=$4

if [ "$name" == "" ]
then
    echo "Use image name airflow_analyze"
    name="airflow_analyze"
fi

if [ "$image" == "" ]
then
    echo "Error,Need docker image path!!!!"
    image=$ECRFULLNAME
fi

if [ "$cpu" == "" ]
then
    echo "Use cpu=1024"
    cpu="1024"
fi

if [ "$memory" == "" ]
then
    echo "Use momory=8192"
    memory="8192"
fi

#create execution role
regions=$(aws configure get region)
role_name="ecsTaskExecutionRole"
execution_role_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
execution_role_arn=$(aws iam get-role --role-name ecsTaskExecutionRole|grep Arn|awk  '{print $2}')
if [ "$execution_role_arn" == "" ]
then
    aws iam --region ${regions} create-role --role-name ${role_name} --assume-role-policy-document file://task-execution-assume-role.json
    aws iam --region ${regions} attach-role-policy --role-name ${role_name} --policy-arn ${execution_role_arn}
fi

(
  #cd "${DIR}/.."
  #REVISION=$(git rev-parse "${BRANCH}")
  #PREVIOUS_TASK_DEF=$(aws ecs describe-task-definition --region "${ECS_REGION}" --task-definition "${ECS_TASK_DEFINITION_NAME}-${ENVIRONMENT}")
  #NEW_CONTAINER_DEF=$(cat ./ecs-task-template.json | python <(cat <<-EOF
  NEW_CONTAINER_DEF=`
python <<EOF
import sys, json
with open('ecs-task-template.json','r') as f:
    taskDefine = json.load(f)
containerDefine = taskDefine['containerDefinitions']
containerDefine[0]['name'] = '${name}'
containerDefine[0]['image'] = '${image}'
#definition[0]['image'] = '${ECR_URI}/${ECR_NAME}:${ENVIRONMENT}-${VERSION}'
taskDefine['cpu'] = '${cpu}'
taskDefine['memory'] = '${memory}'
print(taskDefine)
with open('.ecs-task.json', 'w') as fw:
    json.dump(taskDefine,fw)
EOF
`
  export task_arn=$(aws ecs register-task-definition --region "${regions}" --family "${name}-task" --cli-input-json "file://.ecs-task.json" --execution-role-arn ${execution_role_arn}|grep taskDefinitionArn|awk "{print $2}")
  #aws ecs register-task-definition --region "${regions}" --family "${name}-task" --container-definitions "${NEW_CONTAINER_DEF}"
  #aws ecs update-service --region "${ECS_REGION}" --cluster "${ECS_CLUSTER_NAME}" --service "${ECS_SERVICE_NAME}-${ENVIRONMENT}"  --task-definition "${ECS_TASK_DEFINITION_NAME}-${ENVIRONMENT}"
)