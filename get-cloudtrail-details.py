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
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def get_cloudtrail_details(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    ec2 = session.client("ec2",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]

    report_file = (f"/tmp/{accountName}.cloudtrail_setup.csv")
    with open(report_file, "w") as file:
        file.write(f"NAME;S3BUCKET_NAME;S3KEY_PREFIX;SNS_TOPIC_ARN;INCLUDE_GLOBAL_SERVICES;IS_MULTIREGION;IS_ORGANIZATION_TRAIL;REGION;ACCOUNT_NAME\n")

    regions = [region["RegionName"] for region in ec2.describe_regions()["Regions"]]
    for region in regions:
        cloudtrail = session.client("cloudtrail", region_name=region, config=config)
        trails = cloudtrail.describe_trails()["trailList"]
        for trail in trails:
            trailName = trail.get("Name", "NOT-DEFINED")
            s3bucketName = trail.get("S3BucketName", "NOT-CONFIGURED")
            s3Prefix = trail.get("S3KeyPrefix", "NOT-DEFINED")
            IncludeGlobalServices = trail.get("IncludeGlobalServiceEvents", "NOT-DEFINED")
            MultiRegionalTrail = trail.get("IsMultiRegionTrail", "NOT-DEFINED")
            OrganizationTrail = trail.get("IsOrganizationTrail", "NOT-DEFINED")
            snsTopicARN = trail.get("SnsTopicARN", "NOT-SETUP")
            write_line = (f"{trailName};{s3bucketName};{s3Prefix};{snsTopicARN};{IncludeGlobalServices};{MultiRegionalTrail};{OrganizationTrail};{region};{accountName}")
            with open(report_file, "a") as file:
                print(write_line, file=file)

    print(f"Report saved in {report_file}\nReading file..\n")
    pretty_ssv(report_file)


def pretty_ssv(filename):
    with open(filename) as f:
        rows = list(csv.reader(f, delimiter=';'))
        num_columns = len(rows[0])
        column_widths = [max(len(row[i]) for row in rows) for i in range(num_columns)]
        for row in rows:
            print(' '.join(f'{cell:<{column_widths[i]}}' for i, cell in enumerate(row)))


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      get_cloudtrail_details(profileName)