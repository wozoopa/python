#!/usr/bin/env python

import re
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
pattern = input("\nProvide pattern to search for --> ")
print(f"ROLE_NAME;ROLE_ARN;ACCOUNT_NAME;REGION")

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def find_iam_role(profileName, pattern):
	session = boto3.Session(profile_name=profileName)
	iam = session.client("iam", config=config)

	try:
	    roles = iam.list_roles()
	    account_alias = iam.list_account_aliases()
	    accountName = account_alias['AccountAliases'][0]
	    rName = "us-east-1"

	    paginator = iam.get_paginator('list_roles')
	    page_iterator = paginator.paginate()
	    for page in page_iterator:
	        for role in page['Roles']:
	            rArn = role['Arn']
	            rName = role['RoleName']
	            if re.search(pattern, rName, re.IGNORECASE):
	                print(f"{rName};{rArn};{accountName};{rName}")

	except Exception as e:
	    print(f"ISSUE with listing roles using {profileName} profile with error:\n{e}")


profile_list = read_profile_list(config_file)
for p in profile_list:
	profileName = p.replace('"', '')
	find_iam_role(profileName, pattern)
