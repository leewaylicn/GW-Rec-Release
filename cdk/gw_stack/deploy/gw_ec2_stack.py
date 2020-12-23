from aws_cdk import (
    core, 
    aws_ec2 as ec2, 
    aws_ecs as ecs, 
    aws_ecs_patterns as ecs_patterns, 
    aws_elasticache as ec, 
    aws_rds as rds, 
    aws_iam as iam
)
#ec2_type = "t2.micro"
amzn_linux = ec2.MachineImage.latest_amazon_linux(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX,
                                                              edition=ec2.AmazonLinuxEdition.STANDARD,
                                                              virtualization=ec2.AmazonLinuxVirt.HVM,
                                                              storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE)

class GWec2Stack(core.Stack):
    
    def __init__(self, scope: core.Construct, id: str, 
            vpc: ec2.Vpc, interface_ips:list,subnet_type:str,ec2_type:str,keyName:str,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.instanceids=[]
        if subnet_type=='public':
            ec2subnet_type=ec2.SubnetType.PUBLIC
        elif subnet_type=='private':
            ec2subnet_type=ec2.SubnetType.PRIVATE
            print({"ec2.SubnetType.PRIVATE":ec2subnet_type})
            
            
        for interfaceip in interface_ips:
            instance_name="Kafka"+interfaceip
            instance = ec2.Instance(self, "gwec2"+interfaceip,
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_type),
                            instance_name=instance_name,
                            machine_image=amzn_linux,
                            vpc=vpc,
                            key_name=keyName,
                            private_ip_address = interfaceip,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2subnet_type) 
                            )
            instance.instance.add_property_override("BlockDeviceMappings", [{
                                                "DeviceName": "/dev/xvda",
                                                "Ebs": {
                                                    "VolumeSize": "20",
                                                    "VolumeType": "io1",
                                                    "Iops": "150",
                                                    "DeleteOnTermination": "true"
                                                }
                                            }])
            instance.connections.allow_from_any_ipv4(
                ec2.Port.tcp(22), "Allow ssh from internet")
            self.instanceids.append(instance.instance_id)