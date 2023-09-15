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
pattern = input("\nProvide partial policy name--> ")

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list

print(f"POLICY_NAME;POLICY_ARN;ACCOUNT_NAME;ACCOUNT_NR")

def get_policies(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]

    try:
        paginator = iam.get_paginator('list_policies')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for policy in page['Policies']:
                policyName = policy['PolicyName']
                policyArn = policy['Arn']
                accountNr = policyArn.split('::')[1]
                accountNr = accountNr.split(':')[0]
                if re.search(pattern, policyName, re.IGNORECASE):
                    print(f"{policyName};{policyArn};{accountName};{accountNr}")

    except Exception as e:
      print(f"Issue with listing iam policies in {accountName} with error:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      get_policies(profileName)