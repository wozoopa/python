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
report_file = (f"/tmp/{today}.ListConfigServiceSetup.csv")
with open(report_file, "w") as file:
    file.write(f"S3_BUCKET;CONFIG_SERVICE_ENABLED;RECORDING_ALL_RESOURCES;RECORDING_GLOBAL_RESOURCES;RETENTION_DAYS;ACCOUNT_NAME;REGION\n")


def read_profile_list(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list')
    #profile_list = config.get('multipleProfiles', 'profile_list')
    profile_list = profile_list.split(' ')
    return profile_list


def get_config_service_setup(profileName):
    session = boto3.Session(profile_name=profileName)
    iam = session.client("iam",region_name='us-east-1', config=config)
    account_alias = iam.list_account_aliases()
    accountName = account_alias['AccountAliases'][0]

    ec2 = session.client("ec2", region_name='us-east-1')
    s3 = session.client('s3', config=config)
    list_buckets = s3.list_buckets()
    buckets = list_buckets['Buckets']
    all_bucket_names = []
    config_bucket_name = ""
    pattern = "config-bucket"
    try:
        regions = ec2.describe_regions(Filters=[{ 'Name':'opt-in-status', 'Values': ['opt-in-not-required']}] )
        session = boto3.Session(profile_name=profileName)
        config_bucket_name = ""

        for r in regions['Regions']:
            rname = r['RegionName']
            configservice = session.client("config",region_name=rname, config=config)
            get_channel_info = configservice.describe_delivery_channels()
            delivery_channels = get_channel_info['DeliveryChannels']
            # check if we have s3 bucket setup for config
            if not delivery_channels: # empty list
                config_bucket_name = "NOT-SETUP"
            else:
                for item in delivery_channels:
                    config_bucket_name = item['s3BucketName']

            try:
                get_configuration = configservice.describe_configuration_recorders()
                recorders = get_configuration['ConfigurationRecorders']
                if not recorders:
                    configEnabled = "NOT_ENABLED"
                    allSupported = "N/A"
                    globalResources = "N/A"
                    retention_days = "N/A"
                    write_line = (f"{config_bucket_name};{configEnabled};{allSupported};{globalResources};{retention_days};{accountName};{rname}")
                    with open(report_file, "a") as file:
                        print(write_line, file=file)
                else:
                    configEnabled = "TRUE"
                    for item in recorders:
                        recording_group = item['recordingGroup']
                        allSupported = recording_group['allSupported']
                        globalResources = recording_group['includeGlobalResourceTypes']

                    get_retention = configservice.describe_retention_configurations()
                    retention_configurations = get_retention['RetentionConfigurations']
                    if not retention_configurations:
                        retention_days = "7 years"
                        write_line = (f"{config_bucket_name};{configEnabled};{allSupported};{globalResources};{retention_days};{accountName};{rname}")
                        with open(report_file, "a") as file:
                            print(write_line, file=file)
                    else:
                        for retention_data in retention_configurations:
                            retention_days = retention_data['RetentionPeriodInDays']
                            write_line = (f"{config_bucket_name};{configEnabled};{allSupported};{globalResources};{retention_days};{accountName};{rname}")
                            with open(report_file, "a") as file:
                                print(write_line, file=file)

            except Exception as e:
                configEnabled = "REGION_NOT_SETUP"
                allSupported = "N/A"
                globalResources = "N/A"
                retention_days = "N/A"
                write_line = (f"{config_bucket_name};{configEnabled};{allSupported};{globalResources};{retention_days};{accountName};{rname}")
                with open(report_file, "a") as file:
                    print(write_line, file=file)

    except Exception as e:
        print("Issue with describing regions in " + str(accountName) + " with error: ")
        print(e)


if __name__ == "__main__":
    profile_list = read_profile_list(config_file)
    for p in profile_list:
      profileName = p.replace('"', '')
      get_config_service_setup(profileName)

print(f"REPORT FILE READY in .. {report_file}")