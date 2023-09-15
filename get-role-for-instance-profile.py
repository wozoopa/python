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
instance_profile_name = input("\nProvide instance profile name to search for --> ")

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


print("INSTANCE_PROFILE_NAME;IAM_ROLE_NAME")

def get_role_for_instance_profile(profileName, instance_profile_name):

    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam", config=config)
    get_profile_info = iam.get_instance_profile(InstanceProfileName=instance_profile_name)
    instance_profile_info = get_profile_info['InstanceProfile']
    instance_profile_roles = instance_profile_info['Roles']
    for role_info in instance_profile_roles:
        role_name = role_info['RoleName']
        print(f"{instance_profile_name};{role_name}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      get_role_for_instance_profile(profileName, instance_profile_name)