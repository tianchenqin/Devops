##First thing first, import boto3 python module
import boto3
import sys

session = boto3.session(profile_name='default')  #this part is to create a session object with 'Default' profile KeyName
s3object = session.resource('s3')  #create a s3 object with AWS resource type s3


##the below sample is to list all buckets in S3

for bucketobjects in s3object
print(bucketobjects)

## create a S3 bucket

new_bucket = s3.create_bucket(Bucket='tianchenboto', CreateBucketConfiguration={'LocationConstraint': 'cn-north-1'})
