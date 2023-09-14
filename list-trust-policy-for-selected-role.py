#!/usr/bin/env python

import boto3
import json
import configparser
from botocore.config import Config
from botocore.exceptions import ClientError

config = Config(
    retries = dict(
        max_attempts = 10
    )
)

config_file = '/home/user1/.aws/.python-profiles.conf'
report_file = ("/tmp/role-with-trust.csv")

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = config.get('testProfile', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def list_trust_policy_for_role(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)

    roleName = input("Please prive role name --> ")
    getRole = iam.get_role(RoleName=roleName)
    roleTrust = json.dumps(getRole['Role']['AssumeRolePolicyDocument'], indent=2)

    print(f"Trust policy for {roleName} role\n{roleTrust}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_trust_policy_for_role(profileName)