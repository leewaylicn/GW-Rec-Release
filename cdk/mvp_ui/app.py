#!/usr/bin/env python3

from aws_cdk import core

from armvp.armvp_stack import ArmvpStack


app = core.App()
ArmvpStack(app, "armvp", env={'region': 'us-west-2'})

app.synth()
