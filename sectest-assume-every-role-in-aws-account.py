#! /usr/bin/env python3

import boto3
import configparser
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
report_file = (f"/tmp/{today}.SecTestAssumeRolesReport.csv")
with open(report_file, "w") as file:
    file.write(f"ROLE_NAME;ROLE_PATH;ROLE_ARN;ACCOUNT_NAME;ACCOUNT_NR;RESULT\n")


def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = config.get('testProfile', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def get_roles(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    try:
        account_alias = iam.list_account_aliases()
        accountName = account_alias['AccountAliases'][0]

    except Exception as e:
        accountName = "UNABLE-TO-RETRIEVE-ACCOUNT-NAME"

    sts = session.client("sts", config=config)
    whoami = sts.get_caller_identity()
    my_arn = whoami['Arn']
    if "assumed" in my_arn:
        myRoleName = my_arn.split('/')[1]
        print(f"We are using IAM role: {myRoleName}")
    else:
        myUserName = my_arn.split('/')[1]
        print(f"We are using IAM user: {myUserName}")

    try:
        paginator = iam.get_paginator('list_roles')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for role in page['Roles']:
                roleName = role['RoleName']
                roleArn = role['Arn']
                roleId = role['RoleId']
                rolePath = role['Path']
                accountNr = roleArn.split('::')[1]
                accountNr = accountNr.split(':')[0]
                try:
                    roleSessionName = (f"SecTest_{today}_{roleName}")
                    assume_role = sts.assume_role(RoleArn=roleArn,RoleSessionName=roleSessionName)
                    assume_result = f"WARNING - {profileName} can assume {roleName}"
                    write_line = (f"{roleName};{rolePath};{roleArn};{accountName};{accountNr};{assume_result}")
                    with open(report_file, "a") as file:
                        print(write_line, file=file)

                except Exception as e:
                    assume_result_not_recorded = f"GOOD - UnableToAssumeRole"

    except Exception as e:
        print(f"Issue with listing roles in {accountName} with error:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      get_roles(profileName)


print(f"REPORT FILE READY in .. {report_file}")