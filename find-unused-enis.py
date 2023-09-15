#! /usr/bin/env python3

import boto3
import configparser
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


report_file = ("/tmp/unused-enis.all_accounts.csv")
file = open(report_file, "w")
file.write("ENI;ENI_STATUS;AWS_MANAGED;REQUESTER_ID;TYPE;DESCRIPTION;ACCOUNT_NAME;REGION\n")
file.close()


def find_unused_enis_function(profileName):
    session = boto3.Session(profile_name=profileName)
    ec2 = session.client("ec2", region_name='us-east-1')
    try:
        regions = ec2.describe_regions()
    except Exception as e:
        print(f"ISSUE getting regions using profile {profileName}with error:\n{e}")

    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    file = open(report_file, "a")

    for r in regions['Regions']:
        rname = r['RegionName']
        print(f"Checking {accountName} in {rname} region..")
        ec2_client = session.client("ec2", region_name=rname, config=config)
        try:
            paginator = ec2_client.get_paginator('describe_network_interfaces')
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for networkInterface in page['NetworkInterfaces']:
                    eni_id = networkInterface['NetworkInterfaceId']
                    eni_status = networkInterface['Status']
                    eni_type = networkInterface['InterfaceType']
                    eni_managed = networkInterface['RequesterManaged']
                    try:
                        eni_requester_id = networkInterface['RequesterId']
                    except:
                        eni_requester_id = "N/A"
                    eni_description = networkInterface['Description']
                    file.write(f"{eni_id};{eni_status};{eni_managed};{eni_requester_id};{eni_type};{eni_description};{accountName};{rname}\n")

        except Exception as e:
          file.write(f"ERROR LISTING ENIS;ERROR-GETTING-STATUS;ERROR-GETTING-DATA;ERROR;ERROR;ERROR;{accountName};{rname}\n")
          print(f"ERROR message on {accountName} in {rname} region, with error:\n{e}")

    file.close()


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      find_unused_enis_function(profileName)

print(f"FILE {report_file} is READY")