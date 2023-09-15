#! /usr/bin/env python3

import boto3
import configparser
import datetime
import yaml
import json
import os.path
from botocore.config import Config
from botocore.exceptions import ClientError
from collections import OrderedDict

config = Config(
    retries = dict(
        max_attempts = 10
    )
)
config_file = '/home/user1/.aws/.python-profiles.conf'
today = datetime.date.today()
today = (today.strftime("%F"))

def is_yaml(file):
    try:
        yaml.safe_load(file)
        return True
    except yaml.YAMLError:
        return False


def is_json(file):
    try:
        json.loads(file)
        return True
    except json.JSONDecodeError:
        return False


def ordered_dict_to_json(od):
    return json.dumps(od, indent=4)


def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def get_stacks(profileName):
    session = boto3.Session(profile_name=profileName)
    ec2 = session.client('ec2', region_name='us-east-1', config=config)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    account_name = account_alias['AccountAliases'][0]

    regions = [r['RegionName'] for r in ec2.describe_regions()['Regions']]
    for region in regions:
        try:
            cloudformation = session.client("cloudformation",region_name=region, config=config)
            paginator = cloudformation.get_paginator('list_stacks')
            page_iterator = paginator.paginate(StackStatusFilter=['CREATE_COMPLETE','UPDATE_COMPLETE','UPDATE_ROLLBACK_COMPLETE'])
            for page in page_iterator:
                for stack_summary in page['StackSummaries']:
                    stackId = stack_summary["StackId"]
                    stackName = stack_summary["StackName"]
                    template_file = (f"/tmp/{today}.{stackName}.{account_name}.{region}.tmp")
                    file = open(template_file, "w")
                    download_template = cloudformation.get_template(StackName=stackName)['TemplateBody']
                    file.write(str(download_template))
                    file.close()
                    # determine file format:
                    with open(template_file, 'r') as file:
                        contents = file.read()
                        if "OrderedDict" in contents:
                            print(f"{template_file} is json")
                            od = eval(contents)
                            json_data = ordered_dict_to_json(od)
                            file = open(template_file, "w")
                            file.write(json_data)
                            file.close()
                            base = os.path.splitext(template_file)[0]
                            os.rename(template_file, base + '.json')
                        else:
                            print(f"{template_file} is yaml")
                            base = os.path.splitext(template_file)[0]
                            os.rename(template_file, base + '.yaml')

        except Exception as e:
          print(f"Issue with listing stacks in {region} region, with error:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      get_stacks(profileName)