#! /usr/bin/env python3

import boto3
import configparser
import datetime
from botocore.exceptions import ClientError
from botocore.config import Config

config = Config(
    retries = dict(
        max_attempts = 10
    )
)

config_file = '/home/user1/.aws/.python-profiles.conf'

today = datetime.date.today()
today = (today.strftime("%F"))
report_file = (f"/tmp/{today}.IamRolesAndTheirPolicies.csv")
with open(report_file, "w") as file:
    file.write(f"ROLE_NAME;ROLE_PATH;ROLE_ID;ROLE_ARN;POLICY_NAMES;POLICY_ARNS;POLICY_TYPE;ACCOUNT_NAME;ACCOUNT_NR\n")

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def list_roles_and_their_policies(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client('iam', config=config)
    sts = session.client('sts', config=config)
    aws_account = sts.get_caller_identity().get('Account')
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]

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
                # inline policies
                inline_policies = iam.list_role_policies(RoleName=roleName)['PolicyNames']
                if not inline_policies:
                    policyNames = "NO-INLINE-POLICIES"
                    policyArns = "N/A"
                    policyType = "N/A"
                else:
                    policyNames = inline_policies
                    policyType = "inline"

                write_line = (f"{roleName};{rolePath};{roleId};{roleArn};{policyNames};{policyArns};{policyType};{accountName};{accountNr}")
                with open(report_file, "a") as file:
                    print(write_line, file=file)

                # managed policies
                policyNames = []
                policyArns = []
                managed_policies = iam.list_attached_role_policies(RoleName=roleName)['AttachedPolicies']
                for policy in managed_policies:
                    policyNames.append(policy['PolicyName'])
                    policyArns.append(policy['PolicyArn'])
                    policyType = "managed"

                if not managed_policies:
                    policyNames = "NO-MANAGED-POLICIES"
                    policyArns = "N/A"
                    policyType = "N/A"

                write_line = (f"{roleName};{rolePath};{roleId};{roleArn};{policyNames};{policyArns};{policyType};{accountName};{accountNr}")
                with open(report_file, "a") as file:
                    print(write_line, file=file)

    except Exception as e:
        print(f"Issue with listing roles in {accountName} with error:\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
        profileName = p.replace('"', '')
        list_roles_and_their_policies(profileName)