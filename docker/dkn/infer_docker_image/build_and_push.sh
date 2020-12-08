#!/usr/bin/env bash
# FROM_ACCOUNT_ID 代表了引用的 docker image 在哪个账号下，
# global region SM 用的账号是 763104351884
# 中国 region SM 用的账号是 其他
FROM_ACCOUNT_ID=763104351884
# 这个账号指的是想把 build 出来的 image 放到哪个 账号的 ECR 下，也就是当前使用者的account，跟 aws sts get-caller-identity 返回的 account 一致
ACCOUNT_ID=`aws sts get-caller-identity --query Account --output text`
REGION=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/'`
REPO_NAME=gw-infer

TAG=`date '+%Y%m%d%H%M%S'`

$(aws ecr get-login --no-include-email --region ${REGION} --registry-ids $FROM_ACCOUNT_ID)

docker build -f ./Dockerfile -t $REPO_NAME .

docker tag $REPO_NAME $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com.cn/$REPO_NAME:${TAG}

$(aws ecr get-login --no-include-email --region ${REGION} --registry-ids $ACCOUNT_ID)
aws ecr describe-repositories --repository-names $REPO_NAME || aws ecr create-repository --repository-name $REPO_NAME

docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:${TAG}
