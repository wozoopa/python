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
def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = config.get('testProfile', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


pattern = input("\nProvide partial cfn stack name --> ")
print("CFN_STACK_NAME;STACK_STATUS;ACCOUNT_NAME;REGION")
def find_repository(profileName):
    session = boto3.Session(profile_name=profileName)
    ec2 = session.client("ec2", region_name='us-east-1')
    try:
        regions = ec2.describe_regions()
    except Exception as e:
        print(f"ISSUE getting regions using {profileName} profile with error:\n{e}")

    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    errors = []

    for r in regions['Regions']:
        rname = r['RegionName']
        cfn_client = session.client("cloudformation", region_name=rname, config=config)
        try:
            paginator = cfn_client.get_paginator('list_stacks')
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for stacks in page['StackSummaries']:
                    stackName = stacks['StackName']
                    stackStatus = stacks['StackStatus']
                    if re.search(pattern, stackName, re.IGNORECASE):
                        print(f"{stackName};{stackStatus};{accountName};{rname}")

        except Exception as e:
          message_header = (f"Issue with listing cfn stacks when using {profileName} profile in {rname} region, with error:\n{e}")
          full_message = (f"{message_header}\n")
          errors.append(full_message)

    if(errors):
        for error in errors:
            print(f"\nThere were some errors..\n{error}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      find_repository(profileName)