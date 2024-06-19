import requests
import json
import boto3
import urllib.parse
import os
from datetime import date

ssm = boto3.client('ssm')
s3 = boto3.client('s3')

#Retrieve the Store Parameters variable
branch, owner, repo, workflow_name, ghp_token = (

    ssm.get_parameter(Name=os.environ['branch'])['Parameter']['Value'],
    ssm.get_parameter(Name=os.environ['owner'])['Parameter']['Value'],
    ssm.get_parameter(Name=os.environ['repo'])['Parameter']['Value'],
    ssm.get_parameter(Name=os.environ['workflow_name'])['Parameter']['Value'],
    ssm.get_parameter(Name=os.environ['ghp_token'])['Parameter']['Value'],

)

def validateFile(bucket, filename):

    print('About to validate file=', filename)

    today=date.today()
    print("Today's date=", today)

    filename_list=filename.split("/")
    print('filename_list=', filename_list)

    filename_final=filename_list[-1]
    print('filename_final=', filename_final)

    app_live='Deployment-Backups/Release/app-live/Vizru-App-live-Release-' + str(today)
    print('app_live= {} and filename= {}'.format(app_live, filename))

    chat_system='Deployment-Backups/Release/chatsystem/Vizru-chatSystem-Release-' + str(today)
    print('chat_system= {} and filename= {}'.format(chat_system, filename))

    docker='Deployment-Backups/Release/docker/Vizru-Docker-Release-' + str(today)
    print('docker= {} and filename= {}'.format(docker, filename))

    pdfgen='Deployment-Backups/Release/pdfgen/Vizru-pdfgen-Release-' + str(today)
    print('pdfgen= {} and filename= {}'.format(pdfgen, filename))

    pdfgenv2='Deployment-Backups/Release/pdfgenv2/Vizru-pdfgenv2-Release-' + str(today)
    print('pdfgenv2= {} and filename= {}'.format(pdfgenv2, filename))

    if filename.startswith(app_live.strip()):
        return 's3://' + bucket + '/' + filename
    elif filename.startswith(chat_system.strip()):
        return 's3://' + bucket + '/' + filename
    elif filename.startswith(docker.strip()):
        return 's3://' + bucket + '/' + filename
    elif filename.startswith(pdfgen.strip()):
        return 's3://' + bucket + '/' + filename
    elif filename.startswith(pdfgenv2.strip()):
        return 's3://' + bucket + '/' + filename
    else:
        raise Exception("File {} is invalid in {} bucket, please verify the date or name of your file...".format(filename_final, filename_list[2]))

def lambda_handler(event, context):

    print('branch=' + branch)
    print('owner=' + owner)
    print('repo=' + repo)
    print('workflow_name=' + workflow_name)
    print('ghp_token=' + ghp_token)

    # Listening to s3 events and retrieve the latest object
    bucket = event['Records'][0]['s3']['bucket']['name']
    file = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        response = s3.get_object(Bucket=bucket, Key=file)
        print("CONTENT TYPE: " + response['ContentType'])
    except Exception as f:
        print(f)
        print(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                file, bucket))

    s3_uri=validateFile(bucket, file)
    print('s3_uri=', s3_uri)

    # Github workflow
    deploy_headers = {
        "Accept": "application/vnd.github.everest-preview+json",
        "Authorization": "Bearer " + ghp_token
    }

    API_URL = "https://api.github.com/repos/{}/{}/actions/workflows/{}/dispatches".format(owner, repo, workflow_name)
    print("api_url {}".format(API_URL))

    deploy_body_data = {
        "ref": branch,
        "inputs": {"s3_uri": s3_uri, "environment": "NonProd"}
    }

    response = requests.post(API_URL, headers=deploy_headers, data=json.dumps(deploy_body_data))
    if(response.status_code == 204):
        print('The GitHub Workflow was triggered successfully...')
    else:
        print('The GitHub Workflow failed to be triggered with error code {} [Response: {}]'.format(response.status_code, response.content))
