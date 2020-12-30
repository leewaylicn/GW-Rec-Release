#!/usr/bin/env bash
# FROM_ACCOUNT_ID 代表了引用的 docker image 在哪个账号下，
FROM_ACCOUNT_ID=727897471807
# 这个账号指的是想把 build 出来的 image 放到哪个 账号的 ECR 下，也就是当前使用者的account，跟 aws sts get-caller-identity 返回的 account 一致
#ACCOUNT_ID=`aws sts get-caller-identity --query Account --output text`
#REGION=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/'`

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Get the region defined in the current configuration (default to us-west-2 if none defined)
REGION=$(aws configure get region)

REPO_NAME=gw-dkn-train

TAG=`date '+%Y%m%d%H%M%S'`

aws ecr describe-repositories --repository-names "${REPO_NAME}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${REPO_NAME}" > /dev/null
fi

if [[ $region =~ ^cn.* ]]
then
    registry_id="727897471807"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com.cn"
else
    registry_id="763104351884"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com"
fi

eval $(aws ecr get-login --region ${REGION} --no-include-email)
eval $(aws ecr get-login --registry-ids ${registry_id} --region ${REGION} --no-include-email)


#$(aws ecr get-login --no-include-email --region ${REGION} --registry-ids $FROM_ACCOUNT_ID)

docker build -f ./Dockerfile.cn -t $REPO_NAME .

docker tag $REPO_NAME $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com.cn/$REPO_NAME:${TAG}

$(aws ecr get-login --no-include-email --region ${REGION} --registry-ids $ACCOUNT_ID)
aws ecr describe-repositories --repository-names $REPO_NAME || aws ecr create-repository --repository-name $REPO_NAME

docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com.cn/$REPO_NAME:${TAG}