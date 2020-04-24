#!/usr/bin/python 
"""
Author: Stefan Scheungrab <stefan.2.scheungrab@continental-corporation.com>
Lamdba to insert parameters from ssp to dynamodb, triggered by workflow job
    Parameters:
        task
"""

import datetime
import json
import boto3
from datetime import datetime, timedelta
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def remove_empty_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.iteritems() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d

def create_dynamodb_entry(event, context):
    if (not event['task']):
        time = "{}".format(datetime.now())
        post_data = {
            "account_id": "-",
            "source": context.function_name,
            "title": "unable to execute lambda without task",
            "timestamp": time,
            "severity": "ERROR",
            "message": "Lambda {}, missing paramtert task".format(context.function_name)
        }
        result = lambda_client.invoke(FunctionName="ContiProvToolLogger",InvocationType='Event',Payload=json.dumps(post_data))
        raise Exception("Malformed input. One of the attributes: parameters is empty.")

    lambda_client = boto3.client('lambda')
    dynamodb = boto3.resource("dynamodb")
    time = "{}".format(datetime.now())
    if "task" in event:
        task = event['task']
        current_task = int(task['current_task'])
        if "parameters" in task:
            dynamodb_entry = task['parameters']
            print(dynamodb_entry)
            if 'aws_account_id' not in dynamodb_entry:
                aws_account_id = dynamodb_entry['subscription_id']
                dynamodb_entry['aws_account_id'] = aws_account_id
            else:
                aws_account_id = dynamodb_entry['aws_account_id']
            if dynamodb_entry:
                account_table = dynamodb.Table("conti_prov_accounts")
                account_exists = account_table.get_item(
                    Key={"aws_account_id": aws_account_id}
                )
                if 'Item' in account_exists:
                    task['tasks'][str(current_task)]['completed'] = True
                    task['current_task'] = int(current_task + 1)
                    task['tasks'][str(current_task)]['completed_at'] = time
                    dynamodb.Table("jobs").put_item(Item=task)
                else:
                    account_table.put_item(Item=dynamodb_entry)
                    task['tasks'][str(current_task)]['created_at'] = time
                    dynamodb.Table("jobs").put_item(Item=task)