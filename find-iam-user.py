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
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


pattern = input("\nProvide partial user-name to search for --> ")
header = (f"USERNAME;USERID;ARN;ACCOUNT_NAME")
print(f"{header}")

def find_iam_user(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    try:
        paginator = iam.get_paginator('list_users')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for user in page['Users']:
                userName = user['UserName']
                if re.search(pattern, userName, re.IGNORECASE):
                    userId = user['UserId']
                    userArn = user['Arn']
                    line = (f"{userName};{userId};{userArn};{accountName}")
                    print(f"{line}")

    except Exception as e:
      print(f"ERROR listing IAM users using {profileName} with message:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      find_iam_user(profileName)