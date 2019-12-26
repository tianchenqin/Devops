##First thing first, import boto3 python module
import click
import boto3

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
def list_bucket_objects():
    "list objects in an s3 bucket"
    for obj in s3.Bucket('tianchenboto').objects.all():
        print(obj)

if __name__ == '__main__':
    cli()
