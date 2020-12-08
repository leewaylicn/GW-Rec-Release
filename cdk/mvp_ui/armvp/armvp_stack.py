from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    core
)

from usercollecter import UserCollecter

class ArmvpStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        user_info_collecter = UserCollecter(
            self, 'UserInfoCollecter',
        )

        apigw.LambdaRestApi(
            self, 'Endpoint',
            handler=user_info_collecter.handler,
        )

        # apigw.LambdaRestApi(
        #     user_info_collecter.handler
        # )
