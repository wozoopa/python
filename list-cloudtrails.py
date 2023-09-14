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


header = (f"ACCOUNT_NAME;TRAIL_NAME;TRAIL_REGION;TRAIL_BUCKET;SNS_TOPIC\n")
def list_cloudtrails(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    ec2 = session.client("ec2", region_name='us-east-1')
    report_file = (f"/tmp/{today_filename}.{accountName}.cloudTrails.csv")
    file = open(report_file, "w")
    file.write(header)
    file.close()
    try:
        regions = ec2.describe_regions()
    except Exception as e:
        print(f"ISSUE getting regions using profile {profileName} with error:\n{e}")

    for r in regions['Regions']:
        rname = r['RegionName']
        cloudtrail = session.client("cloudtrail", region_name=rname, config=config)
        get_trails = cloudtrail.describe_trails()
        for trail in get_trails['trailList']:
            trailName = trail['Name']
            trailBucket = trail.get('S3BucketName', 'NOT-DEFINED')
            trailTopic = trail.get('SnsTopicName', 'NOT-DEFINED')
            line = (f"{accountName};{trailName};{rname};{trailBucket};{trailTopic}\n")
            with open(report_file, 'a') as file:
                file.write(line)

    print(f"FILE {report_file} is READY\nReading data..\n")
    pretty_ssv(report_file)


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_cloudtrails(profileName)
