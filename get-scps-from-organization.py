#!/usr/bin/env python

import boto3
import configparser
import json
import os
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


def list_scps(profileName):
    session = boto3.Session(profile_name=profileName)
    org = session.client('organizations', config=config)
    list_scps = org.list_policies(Filter='SERVICE_CONTROL_POLICY')
    for policy in list_scps['Policies']:
        scp_name = policy['Name'].replace(" ", "_")
        scp_content = org.describe_policy(PolicyId=policy['Id'])['Policy']['Content']
        filename = f"{scp_name}.json"
        with open(filename, "w") as file:
            json.dump(scp_content, file, indent=4)
            print(f"Downloaded SCP {scp_name} to {filename}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_scps(profileName)