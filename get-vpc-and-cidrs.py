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

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


print(f"VPC_CIDR;VPC_ID;CUSTOM_OR_DEFAULT_VPC;ACCOUNT_NAME;REGION")

def get_vpc_and_cidrs(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    account_name = account_alias['AccountAliases'][0]
    ec2 = session.client("ec2", region_name='us-east-1')

    try:
        regions = [r['RegionName'] for r in ec2.describe_regions()['Regions']]

        for region in regions:
            ec2_region = session.client('ec2', region_name=region)
            vpcs = ec2_region.describe_vpcs()['Vpcs']

            for vpc in vpcs:
                vpc_cidr = vpc['CidrBlock']
                vpc_id = vpc['VpcId']
                is_default = vpc['IsDefault']
                custom_or_default = "default" if is_default else "custom"

                print(f"{vpc_cidr};{vpc_id};{custom_or_default};{account_name};{region}")

    except Exception as e:
        print(f"Issue with describing vpcs in {account_name} with error:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      get_vpc_and_cidrs(profileName)