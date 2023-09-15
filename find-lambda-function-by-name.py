#! /usr/bin/env python3

import boto3
import configparser
import re
from botocore.config import Config
from botocore.exceptions import ClientError

config = Config(
    retries = dict(
        max_attempts = 10
    )
)
config_file = '/home/user1/.aws/.python-profiles.conf'
pattern = input("\nProvide partial lambda name --> ")

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


print(f"FUNCTION_NAME;FUNCTION_ARN;ACCOUNT_NAME;REGION;RUNTIME;LAST_MODIFIED")

def find_lambda_function(profileName, pattern):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    ec2 = session.client("ec2", region_name='us-east-1')
    try:
        regions = ec2.describe_regions()
    except Exception as e:
        print(f"ISSUE getting regions using profile {profileName} with error:\n{e}")

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
                    runtime = function['Runtime']
                    lastmodified = function['LastModified']
                    if re.search(pattern, functionName, re.IGNORECASE):
                        print(f"{functionName};{functionArn};{accountName};{rname};{runtime};{lastmodified}")

        except Exception as e:
          print(f"ERROR GETTING FUNCTION NAME;ERROR GETTING FUNCTION ARN;{accountName};{rname};ERROR-GETTING-DATA;")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      find_lambda_function(profileName, pattern)