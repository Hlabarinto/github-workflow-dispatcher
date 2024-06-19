# github-workflow-dispatcher

github-workflow-dispatcher is python lambda function used to listen to s3 events in a given bucket and trigger GitHub workflow dispatches events using the api.github.com endpoint.

## Usage

- Setup the below values in your AWS Parameter Store
```bash
branch
owner
repo
workflow name
github token
```

- Define an s3 bucket (s) to be used to upload your files
```bash
s3://fileuploadsuatreach/Deployment-Backups/Release/app-live/
s3://fileuploadsuatreach/Deployment-Backups/Release/chatsystem/
s3://fileuploadsuatreach/Deployment-Backups/Release/docker/
s3://fileuploadsuatreach/Deployment-Backups/Release/pdfgen/
s3://fileuploadsuatreach/Deployment-Backups/Release/pdfgenv2/
```

- Deploy your Lambda function on AWS with an s3 trigger option pointing to the buckets defined above.

- Test your function by uploading a file to your buckets.
