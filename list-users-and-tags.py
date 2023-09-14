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

today = datetime.date.today()
today = (today.strftime("%F"))
config_file = '/home/user1/.aws/.python-profiles.conf'
report_file = (f"/tmp/{today}.users_and_tags.csv")
with open(report_file, "w") as file:
    file.write("USER;EMAIL_TAG;EMAIL_TAG_VALUE;ACCOUNT_NAME;ACCOUNT_NR\n")


def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = config.get('testProfile', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def get_email_tag_from_users(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    sts = session.client("sts",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    print(f"Gathering information from {accountName} ..")

    whoami = sts.get_caller_identity()
    accountNr = whoami['Account']

    users = iam.list_users()
    tags = []
    email_tag_value = ""
    file = open(report_file, "a")

    for user in users['Users']:
        userName = user['UserName']
        # CHECK IF EMAIL TAG EXISTS ( email or Email or ignore case)
        tag_list = iam.list_user_tags(UserName=userName)
        email_tag = list(filter(lambda x:x['Key'] == "email", tag_list["Tags"]))
        email_tag2 = list(filter(lambda x:x['Key'] == "Email", tag_list["Tags"]))

        if len(email_tag) > 0:
          user_email = email_tag[0]["Value"]
          write_line = (f"{userName};email;{user_email};{accountName};{accountNr}")
          with open(report_file, "a") as file:
              print(write_line, file=file)

        elif len(email_tag2) > 0:
          user_email = email_tag2[0]["Value"]
          write_line = (f"{userName};Email;{user_email};{accountName};{accountNr}")
          with open(report_file, "a") as file:
              print(write_line, file=file)
        else:
          user_email = "N/A"
          write_line = (f"{userName};MISSING;{user_email};{accountName};{accountNr}")
          with open(report_file, "a") as file:
              print(write_line, file=file)


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
      get_email_tag_from_users(profileName)

print(f"\n\n")
pretty_ssv(report_file)