##First thing first, import boto3 python module
import click
import boto3
from botocore.exceptions import ClientError
from pathlib import Path 

session = boto3.Session(profile_name='default')
print(session)
s3 = session.resource('s3')

print(s3)

##the below sample is to list all buckets in S3
'''
for bucketobjects in s3.buckets.all():
    print(bucketobjects)
'''
## create a S3 bucket

#new_bucket = s3.create_bucket(Bucket='tianchenboto', CreateBucketConfiguration={'LocationConstraint': session.region_name})

print('---------------------------')  ##分割线
@click.group()
def cli():
    "deploy website to aws"
    pass

@cli.command('list-bucket')  ##define a cli command
def list_buckets():
    "list all S3 buckets"
    for bucketobjects in s3.buckets.all():
        print(bucketobjects)

@cli.command('list-bucket-object')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "list objects in an s3 bucket"
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)

@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "create and configure S3 bucket"
    thisbucket = s3.Bucket(bucket)
    policy = """
    {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws-cn:s3:::%s/*"
        }
    ]
    }
    """ % thisbucket.name
    
    policy = policy.strip()
    pol = thisbucket.Policy()
    pol.put(Policy = policy)

    ws = thisbucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    })
    return

if __name__ == '__main__':
    cli()
