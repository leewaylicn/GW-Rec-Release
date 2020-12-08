import json
import os

import boto3
from boto3.dynamodb.conditions import Key

b3_ddb = boto3.resource('dynamodb')
user_info_table = b3_ddb.Table(os.environ['USER_INFO_TABLE'])
item_tag_table = b3_ddb.Table(os.environ['ITEM_TAG_TABLE'])
_lambda = boto3.client('lambda')

check_threshold = 3

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))

    # resource = event.get("source", None)
    resource = event["path"]
    body_str = json.loads(event["body"])
    print('body: {}'.format(body_str))
    # collect user lick 
    # {
    #     "user_id": xxx,
    #     "info":
    #     {
    #         "gender": xxx
    #         "age": xxx
    #         "occpuation": xxx
    #         "profile": [
    #             "xxx",
    #             "xxx"
    #          ]
    #         "cnt": xxx
    #
    #         "movies": [
    #             "xxx",
    #             "xxx"
    #         ]
    #         "sort": [
    #             "xxx",
    #             "xxx"
    #          ]
    #     }
    # }

    # responce_body = 'initial'
    responce_resource = "test_resource_" + event["path"]
    responce_body_str = "test_body_"
    responce_body = responce_body_str + "_" + responce_resource
    if resource == "/login":
        # collect user information
        user_id = body_str["user_id"]
        user_gender = body_str["gender"]
        user_age = body_str["age"]
        user_occupation = body_str["occupation"]
        # pick up random 3 type as profile
        user_profile_list = []
        # initial value
        cnt = 0
        current_movie_list = []

        user_info_table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression='set #attrName = :attrValue',
            ExpressionAttributeNames = {
                "#attrName" : "info"
            },
            ExpressionAttributeValues={
                ':attrValue': {
                    'gender': user_gender,
                    'age': user_age,
                    'occupation': user_occupation,
                    'profile': user_profile_list,
                    'movies': current_movie_list,
                    'cnt': cnt
                }
            },
            ReturnValues="UPDATED_NEW"
        )
        responce_body = 'update user information!'
    elif resource == "/click":
        user_id = body_str["user_id"]
        movie_id = body_str["movie_id"]
        # info_responce = user_info_table.get_item(
        #     Key={'user': user_id},
        # )
        # update user profile list
        # # login user information
        # user_click_num = user_id + '_click'
        # user_click_movie = user_id + '_movie'
        # read information from dynamoDB
        info_responce = user_info_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        # info_responce = user_info_table.get_item(
        #     Key={'user': user_id},
        # )
        print('read info responce: {}'.format(info_responce))

        print('read json: {}'.format(info_responce['Items']))

        info_dict = info_responce['Items'][0]

        current_cnt = info_dict['info']['cnt']
        current_movie_list = info_dict['info']['movies']
        current_user_profile = info_dict['info']['profile']

        #update_user_profile(movie_id, user_id, current_user_profile)

        if int(current_cnt) == check_threshold-1:
            # trigger inference async
            # send user_id + movie_list to sns to trigger lambda/step function
            print("trigger inference !!!!!")
            # erase user_info_table
            current_cnt = 1
            current_movie_list = [movie_id]
        else:
            print("add new movie id !!!!!")
            current_cnt = current_cnt + 1
            current_movie_list.append(movie_id)

        user_info_table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression='set info.cnt=:c, info.movies=:p',
            ExpressionAttributeValues={
                ':c': current_cnt,
                ':p': current_movie_list
            },
            ReturnValues="UPDATED_NEW"
        )
        responce_body = 'update user collect information!'
    elif resource == "/update":
        user_id = body_str["user_id"]
        info_responce = user_info_table.get_item(
            Key={'user': user_id},
        )

        current_gender = info_responce['Items']['gender']
        current_age = info_responce['Items']['age']
        current_occupation = info_responce['Items']['occupation']
        current_profile_list = info_responce['Items']['profile'][0:3]

        push_list = []

        get_top_n_push(push_list,current_gender)
        get_top_n_push(push_list,current_age)
        get_top_n_push(push_list,current_occupation)
        for current_profile in current_profile_list:
            get_top_n_push(push_list,current_profile)
        
        get_recommender_list(push_list, user_id)

        # udpate push list
        responce_body = 'update push list {} !'.format(push_list)
    
    responce = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': responce_body
    }
    print(responce)

    return responce
    # return json.loads(responce)

def update_user_profile(movie_id, user_id):
    #TODO
    user_profile_list = range(1,30)
    user_info_table.update_item(
        Key={
            'user_id': user_id
        },
        UpdateExpression='set info.profile=:p',
        ExpressionAttributeValues={
            ':p': user_profile_list
        },
        ReturnValues="UDPATE_NEW"
    )

def get_top_n_push(push_list, tag_type):
    #TODO
    # push list
    # {
    #     "item_type": age/gender/...,
    #     "info":
    #     {
    #         "movies": [
    #             "xxx",
    #             "xxx"
    #         ]
    #     }
    # }
    info_responce = item_tag_table.get_item(
        Key={'item_type': tag_type},
    )

    push_list.append(info_responce['Items']['info']['movies'][0])

def get_recommender_list(push_list, user_id):
    info_responce = user_info_table.get_item(
        Key={'user_id': user_id},
    )
    sort_list = info_responce['Items']['info']['sort'][0:4]
    push_list = push_list + sort_list


