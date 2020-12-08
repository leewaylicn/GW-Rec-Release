from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
)


# function:
# 1. user profile
# 2. user click
# 3. update push list

class UserCollecter(core.Construct):

    @property
    def handler(self):
        return self._handler
    
    def __init__(self, scope: core.Construct, id: str, **kwargs):

        super().__init__(scope, id, **kwargs)

        self._user_info_table = ddb.Table(
            self, 'UserInfoTable',
            partition_key={'name': 'user_id', 'type': ddb.AttributeType.STRING}
        )

        self._item_tag_table = ddb.Table(
            self, 'ItemTagTable',
            partition_key={'name': 'item_type', 'type': ddb.AttributeType.STRING}
        )

        self._handler = _lambda.Function(
            self, 'UserCollectHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='usercollect.handler',
            code=_lambda.Code.asset('lambda'),
            environment={
                'USER_INFO_TABLE': self._user_info_table.table_name,
                'ITEM_TAG_TABLE': self._item_tag_table.table_name
            }
        )

        self._user_info_table.grant_read_write_data(self.handler)
        self._item_tag_table.grant_read_write_data(self.handler)

