#!/usr/bin/env bash
# # FROM_ACCOUNT_ID 代表了引用的 docker image 在哪个账号下，
# FROM_ACCOUNT_ID=727897471807
# # 这个账号指的是想把 build 出来的 image 放到哪个 账号的 ECR 下，也就是当前使用者的account，跟 aws sts get-caller-identity 返回的 account 一致
# ACCOUNT_ID=`aws sts get-caller-identity --query Account --output text`
# # REGION=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/'`
# # REGION=$(aws configure get region)
# REGION='cn-north-1'
# REPO_NAME=gw-dkn-train
# TAG=`date '+%Y%m%d%H%M%S'`

# # $(aws ecr get-login --no-include-email --region ${REGION} --registry-ids $FROM_ACCOUNT_ID)
# aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${FROM_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com.cn

# # docker build -f ./recsys_tools/Dockerfile.cn -t $REPO_NAME .
# docker build -t $REPO_NAME .

# REGION=$(aws configure get region)
# docker tag $REPO_NAME $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com.cn/$REPO_NAME:${TAG}

# # $(aws ecr get-login --no-include-email --region ${REGION} --registry-ids $ACCOUNT_ID)
# aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com.cn
# aws ecr describe-repositories --repository-names $REPO_NAME || aws ecr create-repository --repository-name $REPO_NAME

# docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com.cn/$REPO_NAME:${TAG}

#!/usr/bin/env bash
# account_id和region是对应最后要push的ECR
account_id=`aws sts get-caller-identity --query Account --output text`
region=$(aws configure get region)
# repo 相关信息
repo_name=gw-dkn-train
#tag=`date '+%Y%m%d%H%M%S'`
tag="latest"

# 基础镜像相关的account_id以及ecr的地址
if [[ $region =~ ^cn.* ]]
then
    registry_id="727897471807"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com.cn"
else
    registry_id="763104351884"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com"
fi

# login 到基础镜像的ecr
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${registry_uri}

# build image
docker build -t $repo_name . --build-arg REGISTRY_URI=${registry_uri}

# 打tag
docker tag $repo_name $account_id.dkr.ecr.$region.amazonaws.com.cn/$repo_name:${tag}

# login 到自己的ecr
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${account_id}.dkr.ecr.${region}.amazonaws.com.cn
# 判断自己的账户下有没有相应的repo
aws ecr describe-repositories --repository-names $repo_name || aws ecr create-repository --repository-name $repo_name

# push repo
docker push $account_id.dkr.ecr.$region.amazonaws.com.cn/$repo_name:${tag}
