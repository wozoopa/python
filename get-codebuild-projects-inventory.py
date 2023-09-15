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


print(f"CODEBUILD_PROJECT_NAME;IMAGE_VERSION;CONTAINER_TYPE;ACCOUNT_NAME;REGION")
def get_codebuild_inventory(profileName):
    session = boto3.Session(profile_name=profileName)
    ec2 = session.client("ec2", region_name='us-east-1')
    try:
        regions = ec2.describe_regions()
    except Exception as e:
        print(f"ISSUE getting regions using {profileName} profile with error:\n{e}")

    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName= account_alias['AccountAliases'][0]

    for r in regions['Regions']:
        rname = r['RegionName']
        codebuild_client = session.client("codebuild", region_name=rname, config=config)
        try:
            paginator = codebuild_client.get_paginator('list_projects')
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for project in page['projects']:
                    project_name = project
                    project_name = list(project_name.split(" "))
                    get_project_info = codebuild_client.batch_get_projects(names=project_name)
                    for project_data in get_project_info['projects']:
                        container_type = project_data['environment']['type']
                        container_image = project_data['environment']['image']
                        this_project_name = project_data['name']
                        print(f"{this_project_name};{container_image};{container_type};{accountName};{rname}")

        except Exception as e:
          print(f"Issue with listing codebuild projects when using {profileName} profile, with error:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      get_codebuild_inventory(profileName)