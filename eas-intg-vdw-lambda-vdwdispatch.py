from __future__ import print_function
import json
import boto3
import urllib.parse
import re
import os
import string
string.ascii_uppercase

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3')
    client = boto3.client('glue')
    sns = boto3.client('sns')

    buckets = event['Records'][0]['s3']['bucket']['name']
    keys = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print('keys :' + keys)
    print(buckets)
    object_version = s3.Object(buckets, keys).version_id

    prefix1 = keys[0:keys.rfind("/")+1]
    print (prefix1)
    
    print('Version ID  :' + str(object_version))
    response = s3_client.list_object_versions(Bucket=buckets,Prefix=keys)
    print('No of Versions :' + str(len(response['Versions'])))
    
    s3Path = "s3://{0}/{1}".format(buckets, keys)
    print (s3Path)

    files = keys
    keyput = files.split('/')[2]
    fstart = keyput.split('_')[0] + '_'
    fstart = fstart.upper()
    print (fstart)
    if fstart =='KYRIBA_':
        if len(response['Versions']) > 1 :
            print('File version has changed or File already Loaded to Traget table')
        else:
            if prefix1 == 'kyriba/payments/':
                print("Triggering Glue Job..." + 'eas-intg-vdw-gluejob-kyriba_pmt : ' + s3Path)
                client.start_job_run(JobName = 'eas-intg-vdw-gluejob-kyriba_pmt', Arguments = {'--input_file_path' : s3Path})
            elif prefix1 == 'kyriba/checks/':
                print("Triggering Glue Job..." + 'eas-intg-vdw-gluejob-kyriba_chkcashed : ' + s3Path)
                client.start_job_run(JobName = 'eas-intg-vdw-gluejob-kyriba_chkcashed', Arguments = {'--input_file_path' : s3Path})
    else:
        print('Wrong Key Uploaded ....................!')
    
    if prefix1 == 'kyriba/payments/':
        sns.publish(
            TopicArn = 'arn:aws:sns:us-east-1:551462409116:viac-vdw-lambdatopic',
            Subject  = 'New Files uploaded to Bucket: ' + buckets,
            Message  = '\nFile was uploaded to bucket: ' + keyput + '\n eas-intg-vdw-gluejob-kyriba_pmt : Glue job triggered'
            )
    elif prefix1 == 'kyriba/checks/':
        sns.publish(
            TopicArn = 'arn:aws:sns:us-east-1:551462409116:viac-vdw-lambdatopic',
            Subject  = 'New Files uploaded to Bucket: ' + buckets,
            Message  = '\nFile was uploaded to bucket: ' + keyput + '\n eas-intg-vdw-gluejob-kyriba_chkcashed : Glue job triggered'
            )