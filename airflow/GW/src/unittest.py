import config as cfg
import boto3

config = cfg.config
client = boto3.session.Session(profile_name='global').client('ecs')


def run_task():
    ret = client.run_task(**config['run_task'])
    print(ret)


def config_test():
    print(config['ecs_task_definition']['containerDefinitions']['environment'][0]['value'])


config_test()