import json
import pytest

from aws_cdk import core
from armvp.armvp_stack import ArmvpStack


def get_template():
    app = core.App()
    ArmvpStack(app, "armvp")
    return json.dumps(app.synth().get_stack("armvp").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
