import requests
import json
import boto3
import urllib.parse
import os

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

    s3_uri = 's3://' + bucket + '/' + file
    print('Bucket=' + bucket + ' File=' + file + ' s3_uri=' + s3_uri)

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
    print('Status_Code {}, Response {}'.format(response.status_code, response.content))
