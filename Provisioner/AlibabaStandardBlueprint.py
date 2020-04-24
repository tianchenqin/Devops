"""
Test Event example:
{
  "regions": [
    "cn-huhehaote"
  ],
  "post_hook": "free_cidrs",
  "account_type": "Alibaba",
  "blueprint": "continental_facing",
  "Alias": "ali-continental-aa5",
  "zone_size": 26,
  "cn-shanghai": 1,
  "target_ou": "Default",
  "account_id": "1383726376898043",
  "action": "provision",
  "cloud": "alicloud",
  "ADName": "ContiAD"
}
"""
import datetime
from datetime import datetime, timedelta
import requests
import ssl
import json
import boto3
from aws_requests_auth.aws_auth import AWSRequestsAuth
from aws_requests_auth import boto_utils

ssl._create_default_https_context = ssl._create_unverified_context


def find_key(key, dictonary):
    for k, v in dictonary.items():
        if k == key:
            return v
        elif isinstance(v, dict):
            result = find_key(key,v)
            if result:
                return result

def provisioner_api(method, function, data = None):
        

        proxy = {
            'http': 'cias.geoaws.com:8080',
            'https': 'cias.geoaws.com:8080'
        }

        url = "https://vfcprqk1pf.execute-api.eu-central-1.amazonaws.com/dev/alicloud/provisioning/tasks"
        host="vfcprqk1pf.execute-api.eu-central-1.amazonaws.com"
        auth = AWSRequestsAuth(aws_host=host, aws_region='eu-central-1', aws_service='execute-api',**boto_utils.get_credentials())

        if data:
                result = requests.request(method, url, data=data, proxies=proxy, auth=auth) 
        else:
                result = requests.request(method, url, proxies=proxy, auth=auth)
        return result
        
def remove_empty_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.items() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d

def trigger_alibabaprov(event, context):
    # TODO implement
    print(event)
    #regions = find_key('regions', event)
    #regions = ["cn-shanghai"]
    account_id = find_key('alibaba_account_id', event)
    #account_id = "1122659179426165"
    account_type = find_key('account_type', event)
    blueprint_val = find_key('blueprint', event)
    print(blueprint_val)
    #blueprint_val = "common"
    alibaba_account_id  = find_key('alibaba_account_id', event)
    #alibaba_account_id  = "1122659179426165"
    zone_size = find_key('zone_size', event)
    
    
    dynamodb = boto3.resource("dynamodb")
    
    if "task" in event:
        task = event['task']
        target_ou = task['parameters']['request']['target_ou']
        current_task = int(task['current_task'])
    else:
        target_ou = find_key('target_ou', event)
        
    ptask = {}
    
    config = dynamodb.Table("conti_prov_config").get_item(Key={'account_type': account_type})['Item']
    regions = config['blueprint_parameters']['regionByDefault']
    blueprint_params = find_key('blueprint_params', event)
    if (not blueprint_params):
        #config = dynamodb.Table("conti_prov_config").get_item(Key={'account_type': account_type})['Item']
        blueprint_parameters = config['blueprint_parameters_standard']

    blueprint = {
        "account_id": account_id,
        "blueprint": "common",
        "blueprint_parameters": blueprint_parameters,
        "cloud": "alicloud",
        "post_hook": "free_cidrs",
        "action": "provision",
    }
    
    #blueprint['blueprint_parameters']['Alias'] = "{}".format(account_id)
    blueprint['blueprint_parameters']['Alias'] = "conti-{}".format(config['config']['account_id'])
    #blueprint['blueprint_parameters']['Alias'] = "10045"
    blueprint['blueprint_parameters']['role_arn'] = "acs:ram::{}:role/masteraccount".format(account_id)
    ptask['blueprints'] = [ blueprint ]
    
    ptask['regions'] = [regions]
    print("We re printing Ptask")
    print(ptask)
    print("I am the alibaba_account_id")
    print(alibaba_account_id)
    print("I am the account_id")
    print(account_id)
    #FOR SIENCE
    #provdata = json.dumps(remove_empty_from_dict(ptask), indent=4, sort_keys=True, ensure_ascii=False, encoding="utf-8")
    provdata = json.dumps(remove_empty_from_dict(ptask), indent=4, sort_keys=True, ensure_ascii=False)
    print(provdata)

    result = provisioner_api('POST','CreateDeployment',provdata)
    print(result)
    if "task" in event:
        print("hola")
        time = "{}".format(datetime.now())
        task = event['task']
        current_task = int(task['current_task'])
        task['tasks'][str(current_task)]['completed'] = True
        task['current_task'] = int(current_task + 1)
        task['tasks'][str(current_task)]['completed_at'] = time
        dynamodb.Table("jobs").put_item(Item=task)