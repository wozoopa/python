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
        scp_name = policy['Name']
        print(f"{scp_name}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_scps(profileName)