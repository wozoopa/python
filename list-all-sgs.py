#! /usr/bin/env python3

import boto3
import configparser
import csv
import datetime
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
report_file = (f"/tmp/{today}.AllSecurityGroupsAllAccounts.csv")
with open(report_file, "w") as file:
    file.write(f"GROUP_NAME;GROUP_ID;GROUP_DESCRIPTION;FROM_PORT;TO_PORT;CIDR;GROUP_RULE;RULE_DESCRIPTION;VPC_ID;AWS_ACCOUNT_NAME\n")


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
    ec2 = session.client("ec2",region_name='us-east-1', config=config)

    regions = [region["RegionName"] for region in ec2.describe_regions()["Regions"]]
    for rname in regions:
        ec2 = session.client("ec2", region_name=rname, config=config)
        print(f"DEBUG - Gathering Security Groups information from {rname} in {accountName}..")
        try:
            paginator = ec2.get_paginator('describe_security_groups')
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for group in page['SecurityGroups']:
                    groupName = group['GroupName']
                    groupId = group['GroupId']
                    groupDescription = group['Description'] if 'Description' in group else 'EMPTY'
                    vpcId = group['VpcId'] if 'VpcId' in group else 'NOT-ATTACHED-TO-VPC'
                    for rule in group['IpPermissions']:
                        for ip_range in rule['IpRanges']:
                            fromPort = rule['FromPort']
                            toPort = rule['ToPort']
                            ipv4cidr = ip_range['CidrIp']
                            ruleDescription = ip_range.get('Description', 'empty')
                            line = (f"{groupName};{groupId};{groupDescription};{fromPort};{toPort};{ipv4cidr};{rule};{ruleDescription};{vpcId};{accountName}")
                            with open(report_file, "a") as file:
                                print(line, file=file)
                        for ipv6_range in rule['Ipv6Ranges']:
                            fromPort = rule['FromPort']
                            toPort = rule['ToPort']
                            ipv6cidr = ipv6_range['CidrIpv6']
                            ruleDescription = ipv6_range.get('Description', 'empty')
                            line = (f"{groupName};{groupId};{groupDescription};{fromPort};{toPort};{ipv4cidr};{rule};{ruleDescription};{vpcId};{accountName}")
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
