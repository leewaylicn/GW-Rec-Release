#!/bin/bash
# account_id和region是对应最后要push的ECR
account_id=`aws sts get-caller-identity --query Account --output text`
region=$(aws configure get region)
# repo 相关信息
repo_name=gw-graph-infer
#tag=`date '+%Y%m%d%H%M%S'`
tag="latest"

# 基础镜像相关的account_id以及ecr的地址
if [[ $region =~ ^cn.* ]]
then
    registry_id="727897471807"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com.cn"
    account_uri="${account_id}.dkr.ecr.${region}.amazonaws.com.cn"
else
    registry_id="763104351884"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com"
    account_uri="${account_id}.dkr.ecr.${region}.amazonaws.com"
fi

# login 到基础镜像的ecr
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${registry_uri}

cd container
# chmod +x kggraph/train
chmod +x kggraph/serve

# build image
docker build -t $repo_name . --build-arg REGISTRY_URI=${registry_uri}

# 打tag
docker tag $repo_name $account_uri/$repo_name:${tag}

# login 到自己的ecr
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${account_uri}
# 判断自己的账户下有没有相应的repo
aws ecr describe-repositories --repository-names $repo_name || aws ecr create-repository --repository-name $repo_name

# push repo
docker push $account_uri/$repo_name:${tag}
