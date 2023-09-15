#! /usr/bin/env python3

import boto3
import configparser
import datetime
import re
import time
from datetime import date
from botocore.config import Config
from botocore.exceptions import ClientError

config = Config(
    retries = dict(
        max_attempts = 10
    )
)
config_file = '/home/user1/.aws/.python-profiles.conf'
today_filename = datetime.date.today()
today_filename = (today_filename.strftime("%F"))

pattern = input("\nProvide partial role name to search for --> ")
header = (f"ROLE_NAME;ROLE_ARN;ROLE_ID;ACCOUNT_NAME;ACCOUNT_NR;ACCESSED_DAYS_AGO;ACCESSED_DATE;SERVICE_NAME\n")

def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def find_iam_role(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]
    report_file = (f"/tmp/{today_filename}.{accountName}.iamRoles.LastAccessDetails.serviceLevel.csv")
    file = open(report_file, "w")
    file.write(header)
    file.close()
    try:
        paginator = iam.get_paginator('list_roles')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for role in page['Roles']:
                roleName = role['RoleName']
                roleArn = role['Arn']
                roleId = role['RoleId']
                accountNr = roleArn.split('::')[1]
                accountNr = accountNr.split(':')[0]
                if re.search(pattern, roleName, re.IGNORECASE):
                    generate_job_id = iam.generate_service_last_accessed_details(Arn=roleArn, Granularity='SERVICE_LEVEL')
                    get_job_id = generate_job_id['JobId']
                    time.sleep(10)
                    get_last_accessed_details = iam.get_service_last_accessed_details(JobId=get_job_id)
                    last_accessed_date = get_last_accessed_details['ServicesLastAccessed']
                    for item in last_accessed_date:
                        count = item['TotalAuthenticatedEntities']
                        count = int(count)
                        if(count > 0):
                            serviceName = item['ServiceNamespace']
                            if(item['LastAuthenticated']):
                                lastAccessedDate = item['LastAuthenticated']
                                # get today's date
                                today = datetime.date.today()
                                today = (today.strftime("%F"))
                                today_year = today.split('-')[0]
                                today_year = int(today_year)
                                today_month = today.split('-')[1]
                                today_month = int(today_month)
                                today_day = today.split('-')[2]
                                today_day = int(today_day)
                                today = date(today_year, today_month, today_day)
                                # format date of last accessed service
                                last_accessed_date_formatted = str(lastAccessedDate)
                                last_accessed_date_formatted = last_accessed_date_formatted.replace(' ', '')
                                year = last_accessed_date_formatted.split('-')[0]
                                year = int(year)
                                month = last_accessed_date_formatted.split('-')[1]
                                month = int(month)
                                day = last_accessed_date_formatted.split('-')[2].split(':')[0]
                                day_size = len(day)
                                day = day[:day_size - 2]
                                day = int(day)
                                last_accessed_date_formatted = date(year, month, day)
                                # calculate days_ago
                                days_ago = today - last_accessed_date_formatted
                                days_ago = str(days_ago)
                                days_ago = days_ago.split(',')[0]
                                days_ago = (days_ago + " ago")
                                line = (f"{roleName};{roleArn};{roleId};{accountName};{accountNr};{days_ago};{lastAccessedDate};{serviceName}\n")
                                with open(report_file, 'a') as file:
                                    file.write(line)
                        else:
                            serviceName = item['ServiceNamespace']
                            days_ago = "N/A"
                            lastAccessedDate = "N/A"
                            line = (f"{roleName};{roleArn};{roleId};{accountName};{accountNr};{days_ago};{lastAccessedDate};{serviceName}\n")
                            with open(report_file, 'a') as file:
                                file.write(line)

    except Exception as e:
      print(f"Issue with listing iam roles in {profileName}, with error:\n{e}")

    print(f"Report file {report_file} ready")


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      find_iam_role(profileName)