#! /usr/bin/env python3

import boto3
import configparser
import csv
import datetime
import re
from botocore.config import Config
from botocore.exceptions import ClientError

config = Config(
    retries = dict(
        max_attempts = 10
    )
)

config_file = '/home/user1/.aws/.python-profiles.conf'

today = datetime.date.today()
today = (today.strftime("%F"))
report_file = (f"/tmp/{today}.AllSecurityGroupsWithPublicAccess.csv")
with open(report_file, "w") as file:
    file.write(f"GROUP_NAME;GROUP_ID;GROUP_DESCRIPTION;FROM_PORT;TO_PORT;GROUP_RULE;RULE_DESCRIPTION\n")


def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = config.get('testProfile', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def get_security_groups(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]

    ec2 = session.client("ec2", region_name='us-east-1')
    try:
        regions = ec2.describe_regions()
    except Exception as e:
        print(f"ISSUE getting regions using {profileName} profile with error:\n{e}")

    for r in regions['Regions']:
        rname = r['RegionName']
        ec2 = session.client("ec2", region_name=rname, config=config)
        try:
            paginator = ec2.get_paginator('describe_security_groups')
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for group in page['SecurityGroups']:
                    groupName = group['GroupName']
                    groupId = group['GroupId']
                    groupDescription = group['Description'] if 'Description' in group else 'EMPTY'
                    for rule in group['IpPermissions']:
                        for ip_range in rule['IpRanges']:
                            if ip_range['CidrIp'] in ["0.0.0.0/0", "::/0"]:
                                fromPort = rule['FromPort']
                                toPort = rule['ToPort']
                                for description in rule['IpRanges']:
                                    ruleDescription = description['Description'] if 'Description' in description else 'empty'
                                    line = (f"{groupName};{groupId};{groupDescription};{fromPort};{toPort};{rule};{ruleDescription}")
                                    with open(report_file, "a") as file:
                                        print(line, file=file)

                        for ipv6_range in rule['Ipv6Ranges']:
                            if ipv6_range['CidrIpv6'] in ["::/0"]:
                                fromPort = rule['FromPort']
                                toPort = rule['ToPort']
                                for description in rule['Ipv6Ranges']:
                                    ruleDescription = description['Description'] if 'Description' in description else 'empty'
                                    line = (f"{groupName};{groupId};{groupDescription};{fromPort};{toPort};{rule};{ruleDescription}")
                                    with open(report_file, "a") as file:
                                        print(line, file=file)

        except Exception as e:
            print(f"Issue with listing describing security groups in {accountName} in {rname} region with error:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      get_security_groups(profileName)


print(f"REPORT FILE READY in .. {report_file}\n")