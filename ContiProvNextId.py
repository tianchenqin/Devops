import boto3
import json
from datetime import datetime, timedelta

def find_key(key, dictonary):
    for k, v in dictonary.items():
        if k == key:
            return v
        elif isinstance(v, dict):
            result = find_key(key,v)
            if result:
                return result

def get_id(event, context):
    lambda_client = boto3.client('lambda')
    if ('task' in event):
        task = event['task']
    else:
        raise Exception("Malformed input. Parameter missing..")

    if (not find_key('account_id', task)):
        dynamodb = boto3.resource("dynamodb")
        config = dynamodb.Table("conti_prov_config").get_item(Key={'account_type': event['task']['parameters']['request']['account_type']})['Item']
        account_id = int(config['config']['account_id']) + 1
        config['config']['account_id'] = account_id
        dynamodb.Table("conti_prov_config").put_item(Item=config)
        current_task = int(task['current_task'])
        time = "{}".format(datetime.now())
        task['parameters']['account_id'] = str(account_id)
        task['parameters']['account_alias'] = "07wwfmawsroot-{}".format(account_id)
        task['tasks'][str(current_task)]['completed'] = True
        task['tasks'][str(current_task)]['created_at'] = time
        task['current_task'] = int(current_task + 1)
        task['tasks'][str(current_task)]['completed_at'] = time
        dynamodb.Table("jobs").put_item(Item=task)
        post_data = {
            "account_id": str(account_id),
            "title": "Account ID was created".format(account_id),
            "source": context.function_name,
            "timestamp": time,
            "severity": "INFO",
            "message": "account id {} was assigned by job {}".format(account_id,event['task']['UUID'])
        }
        result = lambda_client.invoke(FunctionName="ContiProvToolLogger",InvocationType='Event',Payload=json.dumps(post_data))