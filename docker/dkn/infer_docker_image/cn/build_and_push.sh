#!/usr/bin/env bash
# 这个账号指的是想把 build 出来的 image 放到哪个 账号的 ECR 下，也就是当前使用者的account，跟 aws sts get-caller-identity 返回的 account 一致
ACCOUNT_ID=`aws sts get-caller-identity --query Account --output text`
#REGION=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/'`
region=$(aws configure get region)
REGION=$(aws configure get region)
REPO_NAME=gw-infer

#TAG=`date '+%Y%m%d%H%M%S'`
TAG="latest"

# docker pull tensorflow/serving

if [[ $region =~ ^cn.* ]]
then
    registry_id="727897471807"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com.cn"
else
    registry_id="763104351884"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com"
fi

aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${registry_uri}

docker build -t $REPO_NAME . --build-arg REGISTRY_URI=${registry_uri}

docker tag $REPO_NAME $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com.cn/$REPO_NAME:${TAG}

aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com.cn

aws ecr describe-repositories --repository-names $REPO_NAME || aws ecr create-repository --repository-name $REPO_NAME

docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com.cn/$REPO_NAME:${TAG}
