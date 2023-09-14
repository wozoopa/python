#! /usr/bin/env python3

import boto3
import configparser
from datetime import datetime, timezone, timedelta
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
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = config.get('testProfile', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


print(f"ACCOUNT_NAME;IAM_USER;ACCESS_KEY;KEY_STATUS;EXPIRED_DAYS")
def list_expired_keys(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    now = datetime.now(timezone.utc)
    try:
        users = iam.list_users()['Users']
        for user in users:
            access_keys = iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
            userName = user['UserName']
            for access_key in access_keys:
                create_date = access_key['CreateDate'].replace(tzinfo=timezone.utc)
                accessKeyId = access_key['AccessKeyId']
                accessKeyStatus = access_key['Status']
                # Calculate the number of days since the access key was last used
                if access_key['Status'] == 'Inactive':
                    days_since_last_use = (now - access_key['LastUsedDate'].replace(tzinfo=timezone.utc)).days
                else:
                    days_since_last_use = (now - create_date).days

                if days_since_last_use >= 90:
                    daysExpired = days_since_last_use - 90
                    print(f"{accountName};{userName};{accessKeyId};{accessKeyStatus};{daysExpired}")

    except Exception as e:
        print(f"\n\nThere was a problem listing IAM users with error..\n{e}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      list_expired_keys(profileName)