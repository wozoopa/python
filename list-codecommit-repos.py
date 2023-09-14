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


print(f"REPOSITORY_NAME;ACCOUNT_NAME;REGION")
def list_repositories(profileName):
    session = boto3.Session(profile_name=profileName)
    ec2 = session.client("ec2", region_name='us-east-1')
    try:
        regions = ec2.describe_regions()
    except Exception as e:
        print(f"ISSUE getting regions using profile {profileName} profile with error:\n{e}")

    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    errors = []

    for r in regions['Regions']:
        rname = r['RegionName']
        codecommit_client = session.client("codecommit", region_name=rname, config=config)
        try:
            paginator = codecommit_client.get_paginator('list_repositories')
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for repo in page['repositories']:
                    repoName = repo['repositoryName']
                    print(f"{repoName};{accountName};{rname}")

        except Exception as e:
            repoName = f"{e}"
            print(f"{repoName};{accountName};{rname}")

    if(errors):
        print(f"\n\nThere were some errors..\n{errors}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_repositories(profileName)