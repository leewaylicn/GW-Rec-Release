from aws_cdk import core, aws_ec2
from .redis_helper import GWRedisHelper
from .iam_helper import GWIAMHelper


class CdkInfraStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #create vpc https://233121040379.signin.amazonaws.cn/console
        #self.vpc = aws_ec2.Vpc(self, 'Vpc', nat_gateways=1)
        #env={'region': 'cn-northwest-1', 'account': '233121040379'}

        self.vpc = aws_ec2.Vpc.from_vpc_attributes(
            self, 
            "VPC",
            vpc_id = "vpc-03dd7e12c2b20dc08",
            availability_zones = ['cn-northwest-1a'],
            public_subnet_ids =  ["subnet-082f2fa7f0bd5e32d", 
                                "subnet-027dfd44ed62da3a5",
                                "subnet-0075e0d9b93e1ca81"],
            private_subnet_ids =  ["subnet-00eedfae249c4601d"],                    
            vpc_cidr_block = "10.10.0.0/16",
            private_subnet_route_table_ids=["rtb-03e3e601d120ce62b"]
        )

        #self.vpc = aws_ec2.Vpc.from_lookup(self, "VPC", vpc_id = "vpc-03dd7e12c2b20dc08")
        #core.CfnOutput(self, 'vpcId', value=self.vpc.vpc_id, export_name='ExportedVpcId')

        #create redis
        self.redis_addr, self.redis_port = GWRedisHelper.create_redis(self, self.vpc)

        #create ecs role
        self.ecs_role = GWIAMHelper.create_ecs_role(self)
        
