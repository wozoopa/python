#! /usr/bin/env python3

import boto3
import configparser
from botocore.config import Config
from botocore.exceptions import ClientError

config = Config(
    retries = dict(
        max_attempts = 10
    )
)

config_file = '/home/user1/.aws/.python-profiles.conf'
def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def list_all_lambda_functions(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    account_name = account_alias['AccountAliases'][0]
    ec2 = session.client("ec2", region_name='us-east-1')
    regions = ec2.describe_regions()

    for r in regions['Regions']:
        rname = r['RegionName']
        lambda_client = session.client("lambda", region_name=rname, config=config)
        try:
            paginator = lambda_client.get_paginator('list_functions')
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for function in page['Functions']:
                    functionName = function['FunctionName']
                    functionArn = function['FunctionArn']
                    functionRunTime = function['Runtime']
                    print(f"{functionName};{functionArn};{account_name};{rname};{functionRunTime}")

        except Exception as e:
          print(f"Issue with listing lambda functions in {rname} region, with error:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_all_lambda_functions(profileName)