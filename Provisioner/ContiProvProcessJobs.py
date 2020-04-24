#!/usr/bin/python

"""
Author: Stefan Scheungrab <stefan.2.scheungrab@continental-corporation.com>
Lambda to process a workflow by a job
    Parameters:
	none
"""
import boto3
import json
import decimal
import boto3.dynamodb.types
from time import sleep
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return int(obj)
    raise TypeError

def process_jobs(event, context):
    lambda_client = boto3.client('lambda')
    dynamodb = boto3.resource("dynamodb")
    jobstable = dynamodb.Table("jobs")
    sleep(2)
    jobs = jobstable.scan(
        FilterExpression=Attr('completed').eq(False) 
    )
    for job in jobs['Items']:
        print(job)
        sleep(2)
        current_task = job['current_task']
        if str(current_task) in job['tasks']:
            task = job['tasks'][str(current_task)]
            
            if ('triggered_at' in task):
                time_now = datetime.now()
                created_time = datetime.strptime(task['triggered_at'], "%Y-%m-%d %H:%M:%S.%f")
                timedelta = time_now - created_time

                if (timedelta.total_seconds() / 60 ) >= int(task['time']):
                    job['completed'] = True
                    job['status'] = "FAILED"
                    dynamodb.Table("jobs").put_item(Item=job)
                    #post_data = {
                    #     'task': job
                    #}
                    print("JOB TOOK TO LONG")
                    #    lambda_client.invoke(FunctionName="ContiProvCreateIncident"),InvocationType='Event',Payload=json.dumps(post_data))
                else:
                    retrigger = True
                    if "wait" in task:
                        if (timedelta.total_seconds() / 60 ) <= int(task['wait']):
                            retrigger = False
                    if retrigger:
                        post_data = {
                            'task': job
                        }
                        print(json.dumps(post_data,default=decimal_default))
                        lambda_client.invoke(FunctionName="{}".format(job['tasks'][str(current_task)]['invoke']),InvocationType='Event',Payload=json.dumps(post_data,default=decimal_default))
            else:
                if task['time']:
                    time = "{}".format(datetime.now())
                    job['tasks'][str(current_task)]['triggered_at'] = time
                    dynamodb.Table("jobs").put_item(Item=job)
                post_data = {
                     'task': job
                }
                print(json.dumps(post_data,default=decimal_default))
                lambda_client.invoke(FunctionName="{}".format(job['tasks'][str(current_task)]['invoke']),InvocationType='Event',Payload=json.dumps(post_data,default=decimal_default))
        else:
            job['completed'] = True
            job['status'] = "COMPLETED"
            dynamodb.Table("jobs").put_item(Item=job)