#!/usr/bin/env python3

from aws_cdk import core

# from deploy.gw_stack import GWStack
from deploy.gw_graph_stack import GWGraphStack
from deploy.gw_infra_stack import CdkInfraStack
from deploy.gw_dkn_stack import GWDknStack
from deploy.gw_inferhandler_stack import GWInferHandlerStack
from deploy.gw_sample_stack import GWSampleStack
from deploy.gw_loginto_stack import GWLogintoStack

#from deploy.gw_infra_stack_test import CdkInfraStackTest

# from deploy.gw_trainhandler_stack import GWTrainHandlerStack



app = core.App()
# GWStack(app, "gw-recommendation-stack")
#GWGraphStack(app, "gw-graph-stack")
#GWInferHandlerStack(app, "gw-inferhandler-stack")

#GWGraphStack(app, "gw-graph-stack")
# GWTrainHandlerStack(app, "gw-train-stack")

# infra_stack = CdkInfraStackTest(
#                 app, 
#                 "cdk-stack-infer-infra-test"
#             )

infra_stack = CdkInfraStack(
                app, 
                "cdk-stack-infer-infra-test"
            )

# sample_stack = GWSampleStack(
#                 app, 
#                 "cdk-stack-liwei-sample", 
#                 infra_stack.vpc, 
#                 ecs_role = infra_stack.ecs_role
#             )

dkn_stack = GWDknStack(
            app, 
            "cdk-stack-infer-dkn", 
            infra_stack.vpc,
            ecs_role=infra_stack.ecs_role,
        )

graph_stack = GWGraphStack(
                app, 
                "cdk-stack-infer-graph", 
                infra_stack.vpc
                #ecs_role = infra_stack.ecs_role
            )

# infer_handler_stack = GWInferHandlerStack(
#                         app, 
#                         "cdk-stack-infer-handler", 
#                         infra_stack.vpc, 
#                         ecs_role=infra_stack.ecs_role,
#                         graph_url=graph_stack.graph_inference_dns, 
#                         dkn_url=dkn_stack.url+":8501",
#                         redis_host=infra_stack.redis_addr, 
#                         redis_port=infra_stack.redis_port
#                     )

infer_handler_stack = GWInferHandlerStack(
                        app, 
                        "cdk-stack-infer-handler", 
                        infra_stack.vpc, 
                        ecs_role=infra_stack.ecs_role,
                        graph_url=graph_stack.url+":8080", 
                        dkn_url=dkn_stack.url+":8501",
                        redis_host=infra_stack.redis_addr, 
                        redis_port=infra_stack.redis_port
                    )

# gw_loginto_stack = GWLogintoStack(
#                         app, 
#                         "cdk-stack-loginto", 
#                         infra_stack.vpc, 
#                         ecs_role=infra_stack.ecs_role,
#                         redis_host=infra_stack.redis_addr, 
#                         redis_port=infra_stack.redis_port
#                     )

app.synth()
