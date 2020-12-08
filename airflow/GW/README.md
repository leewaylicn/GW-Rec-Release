# 总体流程
1. 先跑cloudformation，建立相关的 role 等东西，替换掉 config 里的role
2. 创建ECS cluster GW
3. 配置subnet securitygroup
4. 建立 log group

##关于运行 Python CDK
需要先安装node，安装方法参考：
https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/setting-up-node-on-ec2-instance.html

ecs task definition 在定义的时候，有两个地方要注意：
1. 要使用 Optional IAM role
2. 要设置 task 的security group 确保能被VPC 里的其他服务所调用。  


## 关于运行训练
airflow 吊起SM训练本质是通过boto3的，所以要配置一下root用户的 ak sk 才行，否则会包 找不到 bucket的错误：
airflow.exceptions.AirflowException: The input S3 Bucket leigh-gw does not exist 