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
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = config.get('testProfile', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def pretty_ssv(filename):
    with open(filename) as f:
        rows = list(csv.reader(f, delimiter=';'))
        num_columns = len(rows[0])
        column_widths = [max(len(row[i]) for row in rows) for i in range(num_columns)]
        for row in rows:
            print(' '.join(f'{cell:<{column_widths[i]}}' for i, cell in enumerate(row)))


header = (f"INSTANCE_ID;INSTANCE_NAME;REGION;ACCOUNT_NAME;INSTANCE_PROFILE;STARTED_TIME;UPTIME;STATUS\n")
def list_instances_without_iam_roles(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    ec2 = session.client("ec2", region_name='us-east-1')
    report_file = (f"/tmp/{today_filename}.{accountName}.ec2InstancesWithoutIamRole.csv")
    file = open(report_file, "w")
    file.write(header)
    file.close()
    try:
        regions = ec2.describe_regions()
    except Exception as e:
        print(f"ISSUE getting regions using profile {profileName} with error:\n{e}")

    for r in regions['Regions']:
        rname = r['RegionName']
        client = session.client("ec2", region_name=rname, config=config)
        list_instances = client.describe_instances()
        for reservation in list_instances['Reservations']:
            for instance in reservation['Instances']:
                if 'IamInstanceProfile' not in instance:
                    instance_type = instance['InstanceType']
                    launch = instance['LaunchTime']
                    instance_id = instance['InstanceId']
                    instance_state = instance['State']['Name']
                    instance_profile = "NOT-ASSIGNED"

                    if "running" in instance_state:
                        start = str(launch)
                        from datetime import datetime
                        now = datetime.utcnow()
                        # format time:
                        date_format = "%Y-%m-%dT%H:%M:%S"
                        now_formatted = datetime.strftime(now, date_format)
                        now_string = str(now_formatted)
                        now_strip = datetime.strptime(now_string, date_format)
                        launch_time_formatted = datetime.strftime(launch, date_format)
                        launch_time_string = str(launch_time_formatted)
                        launch_time_strip = datetime.strptime(launch_time_string, date_format)
                        ## calculation:
                        uptime = (now_strip - launch_time_strip)
                    else:
                        uptime = "n/a"

                    tags_info = instance["Tags"]
                    for tags in tags_info:
                        if tags["Key"] == 'Name':
                            instance_name = tags["Value"]
                            instance_name = instance_name
                            line = (f"{instance_id};{instance_name};{rname};{accountName};{instance_profile};{launch};{uptime};{instance_state}\n")
                            with open(report_file, 'a') as file:
                                file.write(line)
                        else:
                            instance = "NotSpecified"
                            line = (f"{instance_id};{instance_name};{rname};{accountName};{instance_profile};{launch};{uptime};{instance_state}\n")
                            with open(report_file, 'a') as file:
                                file.write(line)

    print(f"FILE {report_file} is READY\nReading data..\n")
    pretty_ssv(report_file)


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_instances_without_iam_roles(profileName)