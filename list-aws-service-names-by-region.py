#! /usr/bin/env python3

import boto3
import configparser
import csv
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


def list_aws_services(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    ec2 = session.client("ec2",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]

    report_file = (f"/tmp/{accountName}.available_services.csv")
    report_file_log = (f"/tmp/{accountName}.available_services.log")
    with open(report_file, "w") as file:
        file.write(f"SERVICE_NAME;REGION;ACCOUNT_NAME\n")

    regions = [region["RegionName"] for region in ec2.describe_regions()["Regions"]]
    for region in regions:
        ssm = session.client("ssm", region_name=region, config=config)
        path = '/aws/service/global-infrastructure/services/'
        print(f"Checking for available services in {accountName}, {region} region..")
        try:
            paginator = ssm.get_paginator('get_parameters_by_path')
            page_iterator = paginator.paginate(Path=path, Recursive=False, WithDecryption=False)
            for page in page_iterator:
                for param in page['Parameters']:
                    serviceName = param['Name'].split('/')[-1]
                    write_line = (f"{serviceName};{region};{accountName}")
                    with open(report_file, "a") as file:
                        print(write_line, file=file)

        except Exception as e:
            write_line = (f"ISSUE getting parameter from {path} in {region} region with ERROR:\n{e}\nDETAILS of page in paginator:\n{page}\nSERVICE-NAME is:\n {serviceName}")
            with open(report_file, "a") as file:
                print(write_line, file=file)

    print(f"Report saved in {report_file}\nReading file..\n")
    pretty_ssv(report_file)


def pretty_ssv(filename):
    with open(filename) as f:
        rows = list(csv.reader(f, delimiter=';'))
        # Filter out any empty lines or lines with fewer columns than expected
        rows = [row for row in rows if row and len(row) == 3]
        num_columns = len(rows[0])
        column_widths = [max(len(row[i]) for row in rows) for i in range(num_columns)]
        for row in rows:
            print(' '.join(f'{cell:<{column_widths[i]}}' for i, cell in enumerate(row)))


profile_list = read_profile_list(config_file)
for p in profile_list:
  profileName = p.replace('"', '')
  list_aws_services(profileName)

