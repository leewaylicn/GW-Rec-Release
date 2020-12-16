#!/bin/bash

# The name of our algorithm
algorithm_name=recsys-handler-inference

cd container

chmod +x handler/train
chmod +x handler/serve

account=$(aws sts get-caller-identity --query Account --output text)

# Get the region defined in the current configuration (default to us-west-2 if none defined)
region=$(aws configure get region)
region=${region:-cn-north-1}

fullname="${account}.dkr.ecr.${region}.amazonaws.com.cn/${algorithm_name}:latest"

# If the repository doesn't exist in ECR, create it.

aws ecr describe-repositories --repository-names "${algorithm_name}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${algorithm_name}" > /dev/null
fi

# Get the login command from ECR and execute it directly
#$(aws ecr get-login --region ${region} --no-include-email)

if [[ $region =~ ^cn.* ]]
then
    registry_id="727897471807"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com.cn"
else
    registry_id="763104351884"
    registry_uri="${registry_id}.dkr.ecr.${region}.amazonaws.com"
fi

eval $(aws ecr get-login --region ${region} --no-include-email)
eval $(aws ecr get-login --registry-ids ${registry_id} --region ${region} --no-include-email)

#$(aws ecr get-login --region ${region})
#$(aws ecr get-login --registry-ids ${registry_id} --region ${region})

#aws ecr get-login-password --region ${region} |docker login --username AWS --password-stdin ${account}.dkr.ecr.${region}.amazonaws.com
#$(aws ecr get-login-password --region ${region} |docker login -u AWS -e none --password-stdin ${account}.dkr.ecr.${region}.amazonaws.com)
#aws ecr get-login-password --region ${region} |docker login --username AWS --password-stdin ${registry_id}.dkr.ecr.${region}.amazonaws.com
#$(aws ecr get-login-password --region ${region} |docker login -u AWS -e none --password-stdin ${registry_id}.dkr.ecr.${region}.amazonaws.com)

# Build the docker image locally with the image name and then push it to ECR
# with the full name.

docker build  -t ${algorithm_name} . --build-arg REGISTRY_URI=${registry_uri}
docker tag ${algorithm_name}:latest ${fullname}
docker push ${fullname}
