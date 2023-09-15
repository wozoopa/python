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


pattern = input("\nProvide KMS key id to search for --> ")
print(f"KEY_ID;KEY_ALIAS;KEY_ARN;ACCOUNT_NAME;REGION")
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
        kms_client = session.client("kms", region_name=rname, config=config)
        try:
            paginator = kms_client.get_paginator('list_keys')
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for key in page['Keys']:
                    key_id = key['KeyId']
                    key_arn = key['KeyArn']
                    if re.search(pattern, key_id, re.IGNORECASE):
                        try:
                            get_alias = kms_client.list_aliases(KeyId=key_id)['Aliases']
                            for alias in get_alias:
                                key_alias = alias['AliasName']
                                print(f"{key_id};{key_alias};{key_arn};{accountName};{rname}")

                        except Exception as e:
                            key_alias = "NO-ALIAS"
                            print(f"{key_id};{key_alias};{key_arn};{accountName};{rname}")

        except Exception as e:
          print(f"Issue with listing kms keys using {profileName} in {rname}, with error:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      find_lambda_function(profileName, pattern)