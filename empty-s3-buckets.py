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
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = config.get('testProfile', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


bucket_names = input(f"\nProvide bucket names to empty (separated by comma)\nExample: bucket1,bucket2 --> ")
def empty_s3_bucket(profileName, bucket_names):
    session = boto3.Session(profile_name=profileName)
    client = session.client("s3", region_name='us-east-1')
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    s3 = session.client('s3')
    bucket_names = str(bucket_names)
    response = input(f"WARNING: This action cannot be undone. Are you sure you want to delete the following buckets {bucket_names}? (y/n)")
    if response.lower() != "y":
        print("Aborting.")
        exit()

    bucket_names = bucket_names.split(',')

    for bucket_name in bucket_names:
        try:
            paginator = s3.get_paginator('list_object_versions')
            page_iterator = paginator.paginate(Bucket=bucket_name)

            for page in page_iterator:
                if 'DeleteMarkers' in page:
                    delete_markers = [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in page['DeleteMarkers']]
                    s3.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_markers, 'Quiet': True})
                if 'Versions' in page:
                    versions = [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in page['Versions']]
                    s3.delete_objects(Bucket=bucket_name, Delete={'Objects': versions, 'Quiet': True})
        except:
            paginator = s3.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket_name)

            for page in page_iterator:
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})

        s3.delete_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} and all its objects were deleted from {accountName} account.")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      empty_s3_bucket(profileName, bucket_names)