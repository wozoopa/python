#!/usr/bin/env python

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

today = datetime.date.today()
today = (today.strftime("%F"))
config_file = '/home/user1/.aws/.python-profiles.conf'
report_file = (f"/tmp/{today}.iam_users_with_tags_and_policies.csv")

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def list_users_and_their_policies(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    # Initialize CSV file
    csv_file = open(report_file, 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Username', 'EmailTag', 'InlinePolicy', 'ManagedPolicyArn'])
    # List all users
    users_list = iam.list_users(MaxItems=1000)

    # Loop through each user
    for user in users_list['Users']:
        username = user['UserName']
        inline_policies = []
        managed_policy_arns = []

        # Get all policies for the user
        all_policies = iam.list_attached_user_policies(UserName=username)
        if len(all_policies['AttachedPolicies']) > 0:
            # Get managed policy arns
            for policy in all_policies['AttachedPolicies']:
                managed_policy_arns.append(policy['PolicyArn'])
        else:
            managed_policy_arns = "NO-POLICIES"

        # Check if there are inline policies
        all_inline_policies = iam.list_user_policies(UserName=username)
        if len(all_inline_policies['PolicyNames']) > 0:
            inline_policies = all_inline_policies['PolicyNames']
        else:
            inline_policies = "NO-POLICIES"

        tag_list = iam.list_user_tags(UserName=username)
        email_tag = next((tag for tag in tag_list["Tags"] if tag['Key'].lower() == "email"), None)
        if email_tag:
            emailTag = email_tag["Value"]
            if len(emailTag) > 0:
                emailTag = email_tag["Value"]
            else:
                emailTag = "EMPTY"
        else:
            emailTag = "NOT-DEFINED"

        # Write data to CSV
        csv_writer.writerow([username, emailTag, inline_policies, managed_policy_arns])

    csv_file.close()


def pretty_ssv(filename):
    with open(filename) as f:
        rows = list(csv.reader(f, delimiter=','))
        num_columns = len(rows[0])
        column_widths = [max(len(row[i]) for row in rows) for i in range(num_columns)]
        for row in rows:
            print(' '.join(f'{cell:<{column_widths[i]}}' for i, cell in enumerate(row)))


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_users_and_their_policies(profileName)


print(f"\n\n")
pretty_ssv(report_file)