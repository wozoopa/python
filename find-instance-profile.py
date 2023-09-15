#! /usr/bin/env python3

import boto3
import configparser
import csv
import datetime
import re
from botocore.config import Config
from botocore.exceptions import ClientError
from datetime import date

config = Config(
    retries = dict(
        max_attempts = 10
    )
)
config_file = '/home/user1/.aws/.python-profiles.conf'
today_filename = datetime.date.today()
today_filename = (today_filename.strftime("%F"))

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def pretty_ssv(filename):
    with open(filename) as f:
        rows = list(csv.reader(f, delimiter=';'))
        num_columns = len(rows[0])
        column_widths = [max(len(row[i]) for row in rows) for i in range(num_columns)]
        for row in rows:
            print(' '.join(f'{cell:<{column_widths[i]}}' for i, cell in enumerate(row)))


header = (f"INSTANCE_PROFILE_NAME;INSTANCE_PROFILE_ID;INSTANCE_PROFILE_ROLE_NAME;ACCOUNT_NAME\n")
pattern = input("\nProvide partial instance profile to search for --> ")
def find_instance_profile(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    report_file = (f"/tmp/{today_filename}.{accountName}.instanceProfiles.csv")
    file = open(report_file, "w")
    file.write(header)
    file.close()
    try:
        paginator = iam.get_paginator('list_instance_profiles')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for instanceProfile in page['InstanceProfiles']:
                instanceProfileName = instanceProfile['InstanceProfileName']
                instanceProfileId = instanceProfile['InstanceProfileId']
                instanceProfileRoles = instanceProfile['Roles']
                for instanceProfileRole in instanceProfileRoles:
                    instanceProfileRoleName = instanceProfileRole['RoleName']
                if re.search(pattern, instanceProfileName, re.IGNORECASE):
                    line = (f"{instanceProfileName};{instanceProfileId};{instanceProfileRoleName};{accountName}\n")
                    with open(report_file, 'a') as file:
                        file.write(line)

    except Exception as e:
      print(f"ERROR listing instance profiles using {profileName} with message:\n{e}")

    print(f"FILE {report_file} is READY")
    print(f"\n\n")
    pretty_ssv(report_file)


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      find_instance_profile(profileName)