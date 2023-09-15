#! /usr/bin/env python3

import boto3
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
    file.write(f"AWS_SERVICE_NAME;ENDPOINT;REGION\n")


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
    ec2 = session.client("ec2", region_name='us-east-1')
    try:
        regions = ec2.describe_regions()
    except Exception as e:
        print(f"ERROR - Issue listing regions with message:\n{e}")

    for r in regions['Regions']:
        rname = r['RegionName']

        print(f"DEBUG - checking {rname} region")
        ssm = session.client('ssm', region_name=rname, config=config)
        path = f"/aws/service/global-infrastructure/regions/{rname}/services"

        try:
            paginator = ssm.get_paginator('get_parameters_by_path')
            page_iterator = paginator.paginate(Path=path)

            for page in page_iterator:
                for parameter in page['Parameters']:
                    serviceName = parameter['Value']
                    endpointPath = f"{path}/{serviceName}/"
                    print(f"DEBUG - checking for {endpointPath} path")
                    try:
                        endpointInfo = ssm.get_parameters_by_path(Path=endpointPath)['Parameters'][0]['Value']

                    except Exception as e:
                        endpointInfo = "NOT-DEFINED"

                    write_line = (f"{serviceName};{endpointInfo};{rname}")
                    with open(report_file, "a") as file:
                        print(write_line, file=file)

        except Exception as e:
            print(f"ERROR - issue getting parameters in {rname} region with message:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_aws_services(profileName)

print(f"REPORT FILE READY in .. {report_file}")