#! /usr/bin/env python3

import boto3
import csv
import configparser
import datetime
from botocore.exceptions import ClientError
from botocore.config import Config
from typing import List

config = Config(
    retries = dict(
        max_attempts = 10
    )
)

config_file = '/home/user1/.aws/.python-profiles.conf'

today = datetime.date.today()
today = (today.strftime("%F"))
report_file = (f"/tmp/{today}.AwsServices.csv")
with open(report_file, "w") as file:
    file.write(f"AWS_SERVICE_NAME\n")


def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def list_aws_services(profileName):
    session = boto3.Session(profile_name=profileName)
    services = set()
    ssm = session.client('ssm', region_name='us-east-1', config=config)
    path = '/aws/service/global-infrastructure/regions/us-east-1/services'

    paginator = ssm.get_paginator('get_parameters_by_path')
    page_iterator = paginator.paginate(Path=path)

    for page in page_iterator:
        for parameter in page['Parameters']:
            serviceName = parameter['Value']
            write_line = (f"{serviceName}")
            with open(report_file, "a") as file:
                print(write_line, file=file)


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_aws_services(profileName)


print(f"REPORT FILE READY in .. {report_file}")