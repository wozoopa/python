#!/usr/bin/env python

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
pr_number = input("\nProvide PR number to search for --> ")
pr_region = input("\nProvide PR region --> ")

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def find_codecommit_pr(profileName, pr_number, pr_region):
    session = boto3.Session(profile_name=profileName)
    codecommit= session.client('codecommit', region_name=pr_region)

    response = codecommit.list_repositories()
    for repo in response.get('repositories'):
        reponame = repo.get('repositoryName')
        paginator = codecommit.get_paginator('list_pull_requests')
        page_iterator = paginator.paginate(repositoryName=reponame)
        for page in page_iterator:
            ids = page.get('pullRequestIds')
            if pr_number in ids:
                pr_details = codecommit.get_pull_request(pullRequestId=pr_number)['pullRequest']
                #print(f"{pr_details}")
                try:
                    pr_title = pr_details['title']
                    if not pr_details['description']:
                        pr_description = "NO-DESCRIPTION"
                    else:
                        pr_description = pr_details['description']

                except Exception as e:
                    pr_description = "NO-DESCRIPTION"

                pr_status = pr_details['pullRequestStatus']
                pr_author = pr_details['authorArn']
                print(f"PR_TITLE: {pr_title}\nPR_DESCRIPTION: {pr_description}\nPR_STATUS: {pr_status}\nPR_AUTHOR: {pr_author}\nREPOSITORY: {reponame}")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
        profileName = p.replace('"', '')
        find_codecommit_pr(profileName, pr_number, pr_region)