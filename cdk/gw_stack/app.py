#!/usr/bin/env python3

from aws_cdk import core

# from deploy.gw_stack import GWStack
from deploy.gw_graph_stack import GWGraphStack
from deploy.gw_infra_stack import CdkInfraStack
from deploy.gw_dkn_stack import GWDknStack
from deploy.gw_inferhandler_stack import GWInferHandlerStack
from deploy.gw_sample_stack import GWSampleStack
from deploy.gw_loginto_stack import GWLogintoStack
from deploy.gw_recall_stack import GWRecallStack
from deploy.doc_cache import Doccache
from deploy.user_click import UserClick
from deploy.stocks_cache import Stickscache
from deploy.resultapi import Resultapi
from deploy.gw_ec2_stack import GWec2Stack
from deploy.gw_apscheduler_stack  import GWApschedulerStack
from deploy.gw_graph_train_stack  import GWGraphTrainStack
from deploy.gw_dkn_train_stack import GWDknTrainStack

# from deploy.gw_trainhandler_stack import GWTrainHandlerStack

redis_host="redis-gw.inrwks.0001.cnw1.cache.amazonaws.com.cn"
redis_port="6379"
             
app = core.App()
# GWStack(app, "gw-recommendation-stack")
#GWGraphStack(app, "gw-graph-stack")
#GWInferHandlerStack(app, "gw-inferhandler-stack")

#GWGraphStack(app, "gw-graph-stack")
# GWTrainHandlerStack(app, "gw-train-stack")

infra_stack = CdkInfraStack(
                app, 
                "cdk-stack-infer-infra"
                # env={
                #     "region": "cn-northwest-1", 
                #     "account": "233121040379"
                # }
            )
# 私有子网只有一个或者公有子网只有一个
# subnet_type=[public\private]
# subnet_type选择区域，instance_public_ip选择是否配置elp。
ec2_stack = GWec2Stack(
                app, 
                "cdk-stack-infer-ec2", 
                infra_stack.vpc,
                interface_ips=['10.10.20.80','10.10.20.90','10.10.20.95'],
                subnet_type='public',
                ec2_type="t2.micro",
                keyName="eccom-test"
            )

sample_stack = GWSampleStack(
                app, 
                "cdk-stack-infer-Sample", 
                infra_stack.vpc, 
                ecs_role = infra_stack.ecs_role
            )

dkn_stack = GWDknStack(
            app,
            "cdk-stack-infer-dkn",
            infra_stack.vpc,
            ecs_role=infra_stack.ecs_role,
        )
#
graph_stack = GWGraphStack(
                app,
                "cdk-stack-infer-graph",
                infra_stack.vpc,
                redis_host=redis_host,
                redis_port=redis_port
                #ecs_role = infra_stack.ecs_role
            )

# infer_handler_stack = GWInferHandlerStack(
#                         app,
#                         "cdk-stack-infer-handler",
#                         infra_stack.vpc,
#                         ecs_role=infra_stack.ecs_role,
#                         graph_url=graph_stack.graph_inference_dns,
#                         dkn_url=dkn_stack.url+":8501",
#                         redis_host=redis_host,
#                         redis_port=redis_port
#                     )

infer_handler_stack = GWInferHandlerStack(
                        app, 
                        "cdk-stack-infer-handler", 
                        infra_stack.vpc, 
                        ecs_role=infra_stack.ecs_role,
                        graph_url=graph_stack.url+":9008", 
                        dkn_url=dkn_stack.url+":8501",
                        redis_host=redis_host, 
                        redis_port=redis_port
                    )

# handler_url=infer_handler_stack+":8501",
# AWS_PAIXU_URL

gw_loginto_stack = GWLogintoStack(
                        app,
                        "cdk-stack-loginto",
                        infra_stack.vpc,
                        ecs_role=infra_stack.ecs_role,
                        redis_host=redis_host,
                        redis_port=redis_port,
#                         handler_paixu_url = infer_handler_stack.url+ ":8080/invocations"
                    )
#
gw_recall_stack = GWRecallStack(
                        app,
                        "cdk-stack-recall",
                        infra_stack.vpc,
                        ecs_role=infra_stack.ecs_role,
                        redis_host=redis_host,
                        redis_port=redis_port
                    )

doc_cache = Doccache(
                        app,
                        "doc-cache",
                        infra_stack.vpc,
                        ecs_role=infra_stack.ecs_role,
                        redis_host=redis_host,
                        redis_port=redis_port
                    )
#
user_click = UserClick(
                        app,
                        "user-click",
                        infra_stack.vpc,
                        ecs_role=infra_stack.ecs_role,
                        redis_host=redis_host,
                        redis_port=redis_port
                    )
stocks_cache = Stickscache(
                        app,
                        "stocks-cache",
                        infra_stack.vpc,
                        ecs_role=infra_stack.ecs_role,
                        redis_host=redis_host,
                        redis_port=redis_port
                    )
resultapi = Resultapi(
                        app,
                        "resultapi",
                        infra_stack.vpc,
                        ecs_role=infra_stack.ecs_role,
                        redis_host=redis_host,
                        redis_port=redis_port
                    )

gw_apscheduler_stack = GWApschedulerStack(
                        app,
                        "cdk-apscheduler-recall",
                        infra_stack.vpc,
                        ecs_role=infra_stack.ecs_role,
                        redis_host=redis_host,
                        redis_port=redis_port
                    )


############################Deploy training job##################
gw_graph_train_stack = GWGraphTrainStack(
                        app,
                        "cdk-stack-train-graph",
                        infra_stack.vpc
                    )

gw_dkn_train_stack = GWDknTrainStack(
                        app,
                        "cdk-stack-train-dkn",
                        infra_stack.vpc,
                        ecs_role=infra_stack.ecs_role
                    )

app.synth()
